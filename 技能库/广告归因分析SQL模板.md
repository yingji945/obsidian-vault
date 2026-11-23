---
created: 2026-11-23
updated: 2026-11-23
tags: [技能库, SQL模板, 广告归因, 腾讯广告, 自营, 漏斗]
---

# 广告归因分析 · SQL 模板

> **适用**：自营广告投放的归因分析——广告带来的下单人数、订单量、金额，以及下单后的流失拆解
> **来源**：2026-11-23 腾讯广告（tencentad）归因实战（踩了 3 个口径坑，其中 1 个把结论算反了）
> **前置**：广告表在 HBase（`hbase.*`），自营订单表在 Hive（`dw_dws.*`），**同一引擎可 join，跨引擎不行**

---

## 零、开工前必查的三件事

| # | 查什么 | 怎么查 | 影响 |
|:-:|:--|:--|:--|
| 1 | **两张表在哪个引擎** | 各自 `select * from 表 limit 0` | 跨引擎不能 join；`hbase.*` 与 `dw_dws.*` 都在 Hive 侧可跑 |
| 2 | **订单号格式是否一致** | 两边各 `limit 5` 看样本 | 自营 `eorder_no` 是 18 位纯数字，`info_order_no` 也是 ✅ 可直接 join |
| 3 | **`info_event` 各值含义** | 看 `info_request_body` 里的 `action_type` | `6` = `COMPLETE_ORDER`（**下单，不是支付**）|

---

## 一、两张表的结构（实测字段）

### 1.1 `hbase.lucky_ad_click_log` — 广告点击

| 字段 | 样本值 | 含义 |
|:--|:--|:--|
| `rowkey` | `centad-0b5f5shym6bc` | HBase 主键，`来源前缀-click_id` 拼接 |
| `info_create_time` | `2026-11-22 06:34:19` | **点击时间** |
| `info_click_id` | `wx0b5f5shym6bcqw00` | **微信广告 click_id** |
| `info_source` | `tencentad` | 渠道来源 → **限定这个 = 只算自营广告** |
| `info_url` | 一长串 URL 编码 | 落地页 URL，含 `source=S-ZY2`、`sessionId`、`shareTitle` |
| `info_openid` | `null` | ⚠️ 空，**拿不到用户** |
| `info_device_id` | `8765787` | 设备 ID |
| `info_device_type` | `1` | 设备类型 |
| `info_union_id` | `null` | 空 |
| `dt` | `2026-11-22` | 分区 |

### 1.2 `hbase.lucky_ad_event_callback_log` — 转化回调

| 字段 | 样本值 | 含义 |
|:--|:--|:--|
| `rowkey` | `ECL120481879953436672` | HBase 主键，`ECL` + 流水号 |
| `info_callback_time` | `2026-11-22 11:58:34` | 回调时间 |
| `info_result` | `SUCCESS` | 回调结果，说明上报腾讯成功 |
| `info_request_body` | JSON | **回传腾讯的报文全文**（见 1.3）|
| `info_click_id` | `wx03xczu7ydki6ls01` | 关联点击的 key |
| `info_response_body` | `{"code":0,"success":true,...}` | 腾讯返回的响应 |
| `info_event` | `6` | 事件类型 = `COMPLETE_ORDER` |
| `info_ad_channel` | `coffee-tencentad` | 广告账户/渠道标识 |
| `info_order_no` | `120481879559072770` | **= 自营 `eorder_no`** ✅ 已验证 |
| `dt` | `2026-11-22` | 分区（**回调日，不是下单日**）|

### 1.3 `info_request_body` 拆解

```json
{
  "account_id": 46801847,
  "user_action_set_id": 1205223677,
  "actions": [{
    "action_time": 1795319914,          → 2026-11-22 11:58:34（UTC+8）
    "action_type": "COMPLETE_ORDER",    → 下单，不是支付
    "action_param": {"value": 1090},    → 金额，单位「角」= 109.0 元 ⚠️
    "trace": {"click_id": "wx03xczu7ydki6ls01"}
  }]
}
```

🔴 **`action_param.value` 单位是「角」，不是「分」。** 1090 角 = 109.0 元，与自营单均 109.51 元吻合；按「分」理解会差 10 倍。用公式：`round(action_param.value / 10, 2)` 得元。

### 1.4 `info_click_id` 是怎么来的

```
用户点击微信广告
  → 腾讯在落地页 URL 上带 click_id（wx 开头，18 位）
  → 我们接收存进 lucky_ad_click_log
  → 用户下单
  → 我们主动回调腾讯 API，request_body 里带 trace.click_id
  → 同时落一份到 lucky_ad_event_callback_log
```

**三条证据**：① 值以 `wx` 开头（微信广告广点通）；② 回调报文里的 `trace.click_id` 与 `info_click_id` 一字不差；③ `info_source` / `info_ad_channel` 都是 tencentad。

**结论：click_id 由腾讯下发，我们回传时原样带回。** 它是两表唯一的共同字段。

---

## 二、标准 SQL

### 2.1 基础版：下单人数 / 订单量 / 金额

```sql
with click_ids as (
    select distinct info_click_id
    from hbase.lucky_ad_click_log
    where dt = '2026-11-22'
      and info_source = 'tencentad'          -- ← 限定这个 = 只算自营广告
      and info_click_id is not null
      and info_click_id <> ''
),
ad_ord as (
    select distinct c.info_order_no
    from hbase.lucky_ad_event_callback_log c
    join click_ids k
      on c.info_click_id = k.info_click_id
    where c.dt = '2026-11-22'
      and c.info_event = '6'                 -- COMPLETE_ORDER = 下单
      and c.info_order_no is not null
      and c.info_order_no <> ''
),
eord as (
    select eorder_no, mem_id, eorder_income
    from dw_dws.dws_eorder_eorder_d_his_combine
    where dt = date_sub(current_date(), 1)
      and merchant_type = 0
      and eorder_status in ('2','3','7','8','9','10')
      and total_ecmdty_payable_money <> 0
      and eorder_no is not null
    group by eorder_no, mem_id, eorder_income
),
match as (
    select a.info_order_no, e.mem_id, e.eorder_income
    from ad_ord a
    left join eord e on a.info_order_no = e.eorder_no
    where 1 = 1
)
select count(distinct info_order_no)                                        as 广告回调订单数
     , count(distinct case when mem_id is not null then info_order_no end)  as 自营命中订单数
     , round(count(distinct case when mem_id is not null then info_order_no end) * 100.0
             / nullif(count(distinct info_order_no), 0), 2)                 as 命中率_pct
     , count(distinct mem_id)                                               as 下单人数
     , count(distinct case when mem_id is not null then info_order_no end)   as 下单订单量
     , round(sum(eorder_income), 2)                                         as 下单金额
     , round(sum(eorder_income) / nullif(count(distinct mem_id), 0), 2)      as 人均金额
     , round(sum(eorder_income)
             / nullif(count(distinct case when mem_id is not null then info_order_no end), 0), 2) as 单均金额
from match
where 1 = 1
```

### 2.2 两级流失拆解（关键：必须拆开看）

```sql
with click_ids as (
    select distinct info_click_id
    from hbase.lucky_ad_click_log
    where dt = '2026-11-22' and info_source = 'tencentad'
      and info_click_id is not null and info_click_id <> ''
),
ad_ord as (
    select distinct c.info_order_no
    from hbase.lucky_ad_event_callback_log c
    join click_ids k on c.info_click_id = k.info_click_id
    where c.dt = '2026-11-22' and c.info_event = '6'
      and c.info_order_no is not null and c.info_order_no <> ''
)
select case when o.eorder_pay_time is null then '从未支付' else '已支付' end  as 支付状态
     , case when date(o.eorder_pay_time) = '2026-11-22' then '当天'
            when date(o.eorder_pay_time) < '2026-11-22' then '早于当天'
            when date(o.eorder_pay_time) > '2026-11-22' then '晚于当天'
            else '空' end                                              as 相对日
     , o.eorder_status
     , count(distinct a.info_order_no)                                 as 订单数
from ad_ord a
left join dw_dws.dws_eorder_eorder_d_his_combine o
  on a.info_order_no = o.eorder_no
 and o.dt = date_sub(current_date(), 1)
 and o.merchant_type = 0
where 1 = 1
group by case when o.eorder_pay_time is null then '从未支付' else '已支付' end
       , case when date(o.eorder_pay_time) = '2026-11-22' then '当天'
              when date(o.eorder_pay_time) < '2026-11-22' then '早于当天'
              when date(o.eorder_pay_time) > '2026-11-22' then '晚于当天'
              else '空' end
       , o.eorder_status
order by 支付状态, 相对日, o.eorder_status
```

### 2.3 质量对照版：广告 vs 非广告（同口径）

🔴 **必须用 `pay_time` 框两边，才能把「从未支付」的订单同时排除，否则口径不一致。**

```sql
with click_ids as (
    select distinct info_click_id
    from hbase.lucky_ad_click_log
    where dt = '2026-11-22' and info_source = 'tencentad'
      and info_click_id is not null and info_click_id <> ''
),
ad_ord as (
    select distinct c.info_order_no
    from hbase.lucky_ad_event_callback_log c
    join click_ids k on c.info_click_id = k.info_click_id
    where c.dt = '2026-11-22' and c.info_event = '6'
      and c.info_order_no is not null and c.info_order_no <> ''
),
ord as (
    select o.eorder_no, o.mem_id, o.eorder_status
         , case when a.info_order_no is not null then '广告' else '非广告' end as 归因
    from dw_dws.dws_eorder_eorder_d_his_combine o
    left join ad_ord a on o.eorder_no = a.info_order_no
    where o.dt = date_sub(current_date(), 1)
      and o.merchant_type = 0
      and date(o.eorder_pay_time) = '2026-11-22'    -- ← 口径统一的关键
      and o.total_ecmdty_payable_money <> 0
      and o.eorder_no is not null
    group by o.eorder_no, o.mem_id, o.eorder_status
           , case when a.info_order_no is not null then '广告' else '非广告' end
),
hist as (      -- T0 前有有效订单 = 老客
    select distinct mem_id
    from dw_dws.dws_eorder_eorder_d_his_combine
    where dt = date_sub(current_date(), 1)
      and merchant_type = 0
      and eorder_status in ('2','3','7','8','9','10')
      and total_ecmdty_payable_money <> 0
      and mem_id is not null
      and date(eorder_pay_time) < '2026-11-22'
)
select o.归因
     , case when h.mem_id is null then '新客' else '老客' end                              as 用户类型
     , count(distinct o.eorder_no)                                                          as 总单
     , count(distinct case when o.eorder_status in ('2','3','7','8','9','10') then o.eorder_no end) as 有效单
     , count(distinct case when o.eorder_status in ('4','5','6') then o.eorder_no end)       as 取消关闭单
     , round(count(distinct case when o.eorder_status in ('4','5','6') then o.eorder_no end) * 100.0
             / nullif(count(distinct o.eorder_no), 0), 2)                                    as 取消关闭率_pct
from ord o
left join hist h on o.mem_id = h.mem_id
where 1 = 1
group by o.归因, case when h.mem_id is null then '新客' else '老客' end
order by 归因, 用户类型
```

---

## 三、🔴 三个口径陷阱（每一个都会把结论算反）

### 3.1 回调日 ≠ 支付日 ≠ 下单日，三个分母不能混

| 框人群用的字段 | 能框到 | 框不到 |
|:--|:--|:--|
| `callback_log.dt`（回调日）| 所有回调，**含从未支付的单** | 跨天回调的归属会偏 |
| `eorder_pay_time` | 已支付的单 | 🔴 **从未支付的单永远框不到** |
| `eorder_create_time` | 所有下过的单，含未支付 | 需要另算成交 |

**2026-11-22 实测的 70 单差额就是这个陷阱造成的：**

| 口径 | 广告总单 | 有效单 | 取消单 | 取消率 |
|:--|--:|--:|--:|--:|
| 回调日（1,057）| 1,057 | 938 | 119 | 11.26% |
| `pay_time` 当天（987）| 987 | 938 | 49 | 4.97% |
| **差额** | **−70** | **0** | **−70** | |

**这 70 单是 `eorder_pay_time IS NULL` 且 `eorder_status = 5`（订单取消）——它们从来没付过钱，所以按 `pay_time` 框永远看不到。**

### 3.2 取消率有两个都对的答案，看你想回答哪个问题

| 口径 | 分母 | 广告实测 | 回答 |
|:--|--:|--:|:--|
| **A. 全部回调订单** | 1,057 | **11.26%** | 广告带来的下单，最终多少没成交（**漏斗健康度**）|
| **B. 已支付订单** | 987 | **4.97%** | 付了钱之后多少又取消（**履约质量**）|

**做对照时必须两边同一个口径。** 拿广告的口径 A 去比非广告的口径 B，倍数会凭空多出 70%——这是本次实战犯过的错，见第四节。

### 3.3 `COMPLETE_ORDER` 是「下单」不是「支付成功」

腾讯在用户点「提交订单」时就回调，此时还没付钱。所以：

- 回调订单数 **≠** 成交订单数，差额里最大的一块是「从未支付」
- 用 `eorder_status in ('2','3','7','8','9','10')` 才是真正成交口径，别用 `eorder_pay_time is not null`（付了又取消的也会被算进去）

---

## 四、2026-11-22 实测结果（可直接当基准）

### 4.1 核心指标

| 指标 | 值 |
|:--|--:|
| 广告回调下单 | **1,057 单** |
| 支付成功 | **987 单** |
| 最终成交（有效状态）| **938 单** |
| **下单人数** | **922 人** |
| **下单金额** | **102,719.51 元** |
| 人均金额 | 111.41 元 |
| 单均金额 | 109.51 元 |
| **下单→成交率** | **88.74%** |

### 4.2 两级流失

| 层 | 单数 | 流失 | 占比 | 性质 |
|:--|--:|--:|--:|:--|
| 广告回调下单 | 1,057 | — | — | — |
| ├ 从未支付（pay_time 空 + 状态 5）| **70** | −70 | **6.62%** | 🔴 支付环节断掉 |
| 支付成功 | 987 | | | |
| ├ 付后关闭（状态 4）| 43 | | | 🟡 付后反悔 |
| ├ 付后取消售后中（状态 6）| 6 | | | 🟡 付后反悔 |
| 最终成交 | **938** | −49 | **4.97%**（对 987）| |

**两段流失的成因完全不同**：第一段是支付环节问题（跳转失败/价格预期不符），第二段是履约体验问题。修法不一样，不能合并成一句「取消率 11%」。

### 4.3 订单状态分布（1,057 单全部闭合）

| 状态 | 含义 | 单数 | pay_time |
|:--:|:--|--:|:--|
| 2 | 待发货 | 344 | 当天 |
| 3 | 待收货 | 589 | 当天 |
| 10 | 已完成 | 5 | 当天 |
| 4 | 交易关闭 | 43 | 当天 |
| 6 | 取消售后中 | 6 | 当天 |
| **5** | **订单取消** | **70** | 🔴 **空** |
| | | **1,057** | |

### 4.4 质量对照：广告订单质量**更好**，不是更差

口径 B（都按 `pay_time = 11-22`，两边都只含已支付单）：

| 组 | 取消单 | 总单 | 取消率 |
|:--|--:|--:|--:|
| **广告** | **49** | **987** | **4.965%** |
| **非广告** | **333** | **4,060** | **8.202%** |
| 倍数 | | | **1.652×**（广告低 39%）|

`z = −3.449`，`p = 5.63e-04` ✅ 显著

分层后方向一致：

| 用户类型 | 广告 | 非广告 | 倍数 | 显著性 |
|:--|--:|--:|--:|:--|
| 新客 | **6.329%**（30/474）| **9.509%**（250/2,629）| **1.502×** | p=0.026 ✅ |
| 老客 | **3.704%**（19/513）| **5.800%**（83/1,431）| **1.566×** | p=0.068 🟡 |

**成交率对比**：广告 95.04%（938/987）vs 非广告 91.80%（3,727/4,060），广告高 3.24pp。

**含义：广告带来的是目的性更强的用户**（有明确优惠刺激、点击路径直接），自然流量更多是浏览后冲动下单又反悔。这条漏斗健康，**不需要去「修取消率」**。

---

## 五、踩坑记录

| # | ❌ 错 | ✅ 对 | 💡 原因 / 预防 |
|:-:|:--|:--|:--|
| 1 | 只用 `callback_log` 算「广告订单数」，不 join `click_log` | 必须 `join click_log on click_id` 且加 `info_source = 'tencentad'` | 不加渠道过滤，336,014 条回调是全渠道的，自营只占一小块 |
| 2 | 拿「全自营」当广告的对照 | 必须**剔除广告单**后做对照 | 全自营含广告单，是混合值，拿它当基准等于自己比自己 |
| 3 | 广告用回调日分母（1,057）、非广告用 `pay_time` 分母（4,060）比取消率 | 两边必须同一个框人群字段 | 实测这条错让取消率从 4.97% 虚高到 11.26%，**倍数从「低 1.65 倍」翻成「高 1.71 倍」，结论完全反向** |
| 4 | `action_param.value` 当「分」用 | 单位是**角**，`/10` 才是元 | 按分算差 10 倍（10.90 vs 109.0 元）|
| 5 | 以为 `info_order_no` 不是自营订单号（因它与 rowkey 前 9 位相同）| 就是 `eorder_no`，18 位纯数字，命中率 100% | 流水号编码前缀相同是巧合，不能当判据。**验字段要用数据，不能靠格式猜测** |
| 6 | 只算「取消率」一个数 | 必须拆「从未支付」和「付后取消」两段 | 前者是支付环节问题，后者是履约问题，业务动作完全不同 |
| 7 | 用 `eorder_pay_time is not null` 当成交口径 | 用 `eorder_status in ('2','3','7','8','9','10')` | 付了又取消的单也有 pay_time，会被误算成交 |

---

## 六、还没闭合的

| 项 | 状态 |
|:--|:--|
| 「从未支付 6.62%」是否异常 | 🔴 缺非广告对照。要用 `eorder_create_time` 框人群才能看到自然流量的从未支付率 |
| 归因窗口 | 🔴 未知。点击后多少天内的下单还算这次点击，需问投放侧 |
| 同一 `click_id` 多次回调 | 🟡 已用 `distinct info_order_no` 去重，但同一人多单的重复归因未验证 |
| `info_url` 里的 `source=S-ZY2` | 🟡 疑似广告计划/渠道码，含义未确认 |

---

关联：[[技能库索引]] · [[SQL经验库]] · [[门店即享复购分析SQL模板]] · [[引流品转化评估SQL模板]] · [[运营数据分析方法论]] · [[数据字典索引]]
