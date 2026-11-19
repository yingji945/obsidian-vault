---
created: 2026-11-18
updated: 2026-11-18
tags: [技能库, SQL模板, 门店即享, 复购分析, 漏斗]
---

# 门店即享复购分析 · SQL 模板

> **适用**：门店侧商品的「首次购买 → 后续复购」分析（门店复购 / 线上自营复购 / 公域复购），以及门店即享商品的曝光-点击-下单漏斗
> **来源**：2026-11-18 SP4386 咖啡液渠道价值评估实战（跑了 12 组 SQL，踩了 8 个坑）

---

## 零、开工前必查的四件事

| # | 查什么 | 怎么查 | 影响 |
|:-:|:--|:--|:--|
| 1 | **表在哪个引擎** | Hive / Doris 各跑一次 `select 1 from 表 limit 0` | 跨引擎不能 join；`ads_inst_*` 在 **Doris**，`dwm_*` / `dws_*` 在 **Hive** |
| 2 | **商品/套餐的识别字段** | 探针：`select cmdty_code, cmdty_name, package_code, package_id ... group by` | 套餐用 **`package_code`**（`PF%` / `CHPF%`），**不是 `package_id`**（后者全空）|
| 3 | **各品上线日** | 问人，或 `min(dt)` | 上线日不同 → 观察窗口不同 → **不能直接比复购周期**（左截断）|
| 4 | **有效订单口径** | 见第一节 | 少了会多算 1~2% 退款/损耗单 |

---

## 一、标准口径（门店侧）

```sql
-- 有效订单：已支付 ≠ 有效
and order_pay_time is not null
and order_status = 50
and order_cmdty_situation <> 2      -- 排除损耗
and city_name in ('广州', '杭州')
and mem_id is not null
```

**即享商品编码池（7 个）**：

```sql
SP4339  生椰拿铁咖啡饮料 300mL
SP4384  柚C美式咖啡饮料 300mL
SP4386  浓缩咖啡液·意式黑咖 2 颗      ← 主力品
SP4387  浓缩咖啡液·意式黑咖 8 颗
SP4388  冻干咖啡·深烘黑咖啡 18 袋
SP4379  意式拼配咖啡豆 500g
SP4469  浓缩咖啡液·生椰风味 2 颗      ← 2026-11-05 才上线
```

**即享售卖门店**：

```sql
select dept_id
from dw_dim.dim_cmdty_shop_feature_d_his
where dt = date_sub(current_date(), 1)
  and shop_feature_name = '即享咖啡售卖'
group by dept_id
```

> ⚠️ 这是「**今天**在卖即享的门店」快照。若期间有关店/停售，历史订单会被过滤掉。当前门店稳定，影响可忽略；如果项目期长或门店有变动，需改成按历史分区取。

---

## 二、骨架：门店首次购买 → 某渠道复购

### 2.1 结构总览

```
params          时间参数，集中一处
inst_shops      即享售卖门店
shop_buyers     ← 核心：首次购买目标商品的人 + T0
                  （选人池，下游全部引用它）
[可选] new_users  只保留电商自营新客（anti-join T0 前购买）
re_buy          T0 之后的复购行为
base            shop_buyers LEFT JOIN re_buy（保住未复购的人）
final           汇总指标
```

### 2.2 可复制骨架

```sql
with params as (
    select '2026-10-12' as start_d
         , '2026-11-18' as end_d
         , '2026-11-18' as obs_end
),
inst_shops as (
    select dept_id
    from dw_dim.dim_cmdty_shop_feature_d_his
    where dt = date_sub(current_date(), 1)
      and shop_feature_name = '即享咖啡售卖'
    group by dept_id
),

-- ① 首次购买 + T0（唯一选人入口）
shop_buyers as (
    select t.mem_id
         , min(date(t.order_pay_time)) as t0
    from dw_dwm.dwm_mg_order_cmdty_market_wide_d_view t
    join inst_shops s on t.dept_id = s.dept_id
    cross join params p
    where t.dt >= p.start_d
      and t.dt <= p.end_d
      and date(t.order_pay_time) >= p.start_d
      and date(t.order_pay_time) <= p.end_d
      and t.order_pay_time is not null
      and t.order_status = 50
      and t.order_cmdty_situation <> 2
      and t.city_name in ('广州', '杭州')
      and t.mem_id is not null
      and t.cmdty_code = 'SP4386'
    group by t.mem_id
),

-- ② 复购（门店 / 线上自营 / 公域 各自换这一段）
re_buy as (
    select b.mem_id
         , min(datediff(date(t.order_pay_time), b.t0))       as 首复购天数
         , count(distinct date(t.order_pay_time))            as 复购天数
         , count(distinct t.order_id)                        as 复购单数
         , count(distinct t.cmdty_code)                      as 复购品数
         , round(sum(t.cmdty_pay_amt), 2)                    as 复购金额
    from shop_buyers b
    join dw_dwm.dwm_mg_order_cmdty_market_wide_d_view t
      on t.mem_id = b.mem_id
    join inst_shops s on t.dept_id = s.dept_id
    cross join params p
    where t.dt >= p.start_d
      and t.dt <= p.obs_end
      and t.order_pay_time is not null
      and t.order_status = 50
      and t.order_cmdty_situation <> 2
      and t.city_name in ('广州', '杭州')
      and t.cmdty_code in ('SP4339','SP4384','SP4386','SP4387','SP4388','SP4379','SP4469')
      -- 🔴 关键：T0 之后，且排除 T0 当天买同一商品（那是首次购买本身）
      and datediff(date(t.order_pay_time), b.t0) > 0
    group by b.mem_id
),

base as (
    select b.mem_id, b.t0
         , r.首复购天数, r.复购天数, r.复购单数, r.复购品数, r.复购金额
    from shop_buyers b
    left join re_buy r on b.mem_id = r.mem_id      -- LEFT：保住未复购的人做分母
    where 1 = 1
)

select count(distinct mem_id)                                                  as 总人数
     , count(distinct if(复购单数 > 0, mem_id, null))                           as 复购人数
     , round(count(distinct if(复购单数 > 0, mem_id, null)) * 100.0
             / count(distinct mem_id), 2)                                       as 复购率
     , round(sum(复购金额), 2)                                                  as 复购金额
     , round(sum(复购金额) / nullif(count(distinct if(复购单数 > 0, mem_id, null)), 0), 2) as 复购客单价
     , round(avg(if(复购单数 > 0, 首复购天数, null)), 1)                         as 平均首复购天数
     , round(avg(if(复购单数 > 0, 复购品数, null)), 1)                           as 平均复购品数
from base
where 1 = 1
```

---

## 三、五条硬规则（每条都踩过坑）

### 规则 1：T0 当天那一单必须排除

**症状**：含当天复购率算出 **100%**，复购人数 = 总人数。

**原因**：T0 就是「买目标商品那天」，如果复购条件用 `>= t0`，那笔首次购买就被当成复购算回去了——自我循环。

**正确写法**：

```sql
-- 严格口径
and datediff(date(t.order_pay_time), b.t0) > 0

-- 宽松口径（含 T0 当天，但排除目标商品本身）
and not (t.cmdty_code = 'SP4386' and datediff(date(t.order_pay_time), b.t0) = 0)
```

`re_buy` 里必须**先筛掉不合格的行**再统计，否则 `count(o.mem_id)` 会把整个池子算成复购。

---

### 规则 2：不同 T0 的人必须给同样长的窗口

**症状**：按时间切段比复购率，得出「早期用户更会复购」这类结论，但换个切法结论就反了。

**原因**：`t0` 晚的人观察期天然短，复购率必然被压低。按时间段分组等于把「人群质量」和「观察期长度」混在一起。

**正确写法**：统一切到某个固定窗口，并把人限制在「能拥有完整窗口」的范围内：

```sql
-- 想要 T0 + 7 天窗口 → 只留 t0 <= obs_end - 7 的人
and t.dt <= '2026-11-11'
...
and datediff(date(t.order_pay_time), b.t0) <= 7
```

**实战数据**：SP4386 五周 7 天复购率 17.77% / 15.76% / 12.17% / 18.07% / 12.54%，**无趋势**，围绕 15% 波动。用时间切段法会得出完全错误的「早期更好」结论。

---

### 规则 3：比较不同商品前，先查上线日（左截断）

**症状**：SP4469 生椰的「平均首复购 13.8 天」，主力品 SP4386 只有 6.1 天，差点得出「生椰是零食、意式是口粮」的结论。

**原因**：SP4469 **11-05 才上线**，观察期只有 13 天。任何人的生椰复购天数都不可能小于 `11-05 − t0`，这个 13.8 天是被窗口强行拉长的，不是真实周期。

**正确做法**：把所有品统一切到**最晚上线那个品的窗口长度**：

```sql
-- 最晚上线日 11-05，观察截止 11-18 → 13 天
and date(t.order_pay_time) >= '2026-11-05'
```

**实战结果**：统一切到 13 天后，SP4386 13.76%、SP4469 6.19% —— 生椰不但不慢，还是第二受欢迎。

---

### 规则 4：漏斗要严格，每级都带累积条件

**症状**：下单人数 > 商品点击人数，漏斗倒挂。

**原因**：各级都用 `count(distinct if(flag = 1, mem_id, null))`，统计的是「当天有该行为的**所有人**」，各级之间没有约束。有人没点击过，但从历史订单/收藏直达商详下单，就被算进「下单人数」。

**正确写法**（累积条件）：

```sql
, count(distinct if(bw = 1, mem_id, null))                                     as L1_曝光
, count(distinct if(bw = 1 and ck = 1, mem_id, null))                          as L2_点击
, count(distinct if(bw = 1 and ck = 1 and card_ck = 1, mem_id, null))          as L3_卡片点击
, count(distinct if(bw = 1 and ck = 1 and card_ck = 1 and detail_bw = 1
                    , mem_id, null))                                           as L4_商详
, count(distinct if(bw = 1 and ck = 1 and card_ck = 1 and detail_bw = 1
                    and pay_mem = 1, mem_id, null))                            as L5_支付
```

**两个必说的副作用**：

- 严格漏斗按天算时人数会很小，因为要求全链路**同一天**完成（今天曝光、明天点、后天买就断链）。必须同时给「周期严格漏斗」版本，并说清报数用的是哪个
- 金额也只能算「走完全链路的人」的金额：`sum(if(<全部条件>, pay_amt, 0))`

---

### 规则 5：口径不一致的数字，不许运算

**症状**：用「人均售价」当成本；用不同长度窗口比复购周期；用不同人群的复购人数做减法。

**原因**：数字看着都对，但它们是两把不同的尺子量出来的。

**自检清单**（做任何加减乘除前过一遍）：

| 问自己 | 反例 |
|:--|:--|
| 两个数的**分母人群**一致吗？ | 938 人（7,057 分母）− 389 人（2,827 分母）→ 无意义 |
| 两个数的**观察窗口**一致吗？ | 6.1 天（37 天窗口）vs 13.8 天（13 天窗口）→ 不可比 |
| 这个数是**收入**还是**成本**？ | 把人消费付 7.82 元当采购成本 → 错 |
| 这个数是**人次**还是**人数**？ | 34.7% 人次占比 ≠ 人数占比 |
| 这个数是**应付**还是**实付**？ | `cmdty_pay_amt`（应付）vs `new_user_pay_money`（实付），差 0.44~3.23 元 |

---

## 四、即享行为宽表的漏斗写法（`ads_inst_mem_*_behavior_d_1d_uniq`）

两张表，**都在 Doris**：

| 表 | 维度 | 字段数 | 关键字段 |
|:--|:--|--:|:--|
| `ads_inst_mem_**dept**_behavior_d_1d_uniq` | 日 × 人 × 门店 | 26 | `dept_id` / `city_name` / `first_channel_name` / `third_channel_name` / `is_inst_sale_shop` |
| `ads_inst_mem_**cmdty**_behavior_d_1d_uniq` | 日 × 人 × 商品 | 19 | `cmdty_code` / `cmdty_name`，**无渠道/城市/门店字段** |

### 4.1 为什么要 left join 两表

只有私域资源位产生曝光点击数据。**给曝光侧加渠道过滤会把它清空。**

- `cmdty` 版取商品级四级行为（曝光/点击/卡片点击/商详曝光），**不加渠道过滤**
- `dept` 版筛出「私域 + app/微信小程序」人群池，用 `left join` 限定**下单**侧
- 关联键：`dt + mem_id`

```sql
from beh b
left join user_pool u
       on b.dt = u.dt
      and b.mem_id = u.mem_id
where 1 = 1
-- 曝光/点击：全量（b 侧，不加 u 的条件）
-- 下单/金额：加 u.mem_id is not null
```

### 4.2 三个坑

| 坑 | 说明 |
|:--|:--|
| `is_inst_ord_mem` 语义随表变 | `dept` 版是**人级**「此人当日有即享订单」；`cmdty` 版是**商品行级**「此人当日下了这个商品」。同名不同义 |
| 金额字段要分清 | `inst_cmdty_income_pay_amt` = 即享品类金额（干净）；`inst_ord_cmdty_income_pay_amt` = `dept` 版是整单金额、`cmdty` 版是**按行分摊** |
| Doris 语法 | `group by` 用别名不用序号；`count(distinct if(...))` 报错时改 `count(distinct case when ... then x end)` |

---

## 五、输出模板：一句结论 + 三条路径对比

```markdown
| 路径 | 复购率 | 观察口径 | 相对效率 |
|:--|--:|:--|:--|
| <基准渠道> | x.xx% | N 天 | 基准 1× |
| 门店 → 门店 | x.xx% | 统一 7 天 | ?× |
| 门店 → 线上自营 | x.xx% | N 天 | 1/?× |
| 门店 → 公域 | x.xx% | N 天 | 1/?× |
```

**必须同时给出的三个数**：

1. **复购率**（用统一窗口的那个口径）
2. **复购客单价**（否则「复购率高」可能是小额补货）
3. **平均首复购天数**（决定触达时点）

只有复购率没有客单价，会得出「16.27% 复购率不错」的误判——实际客单价只有 11.72 元。

---

> 关联：[[SQL经验库]] · [[门店即享渠道价值评估-SP4386]] · [[运营数据分析方法论]] · [[数据字典索引]]
