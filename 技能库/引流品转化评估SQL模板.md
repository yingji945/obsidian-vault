---
created: 2026-11-05
updated: 2026-11-05
tags: [SQL, 技能库, 数据分析, 引流品, 转化分析, 试用装]
---

# 引流品 / 试用装转化评估 SQL 模板

> **适用场景**：评估低价引流品（试用装、小样、9.9 元档、券包）的真实拉新与转化价值。
> **一句话方法**：把「有多少人领了」换成「**90 天内有多少人真花钱买了正装**」，再算成每 1,000 人的净得。
> **首个实战案例**：[[试用装转化分析-P04672-000003]]

---

## 一、四个必答问题（缺一个结论就不成立）

| # | 问题 | 不搞清的后果 |
|:-:|:--|:--|
| 1 | **引流品本身赚钱还是保本？** | 决定它是"零成本获客"还是"花钱买线索"，判断完全相反 |
| 2 | **观察窗口给多长？** | 30 天口径会低估 **50% 以上**（实测 4.45% vs 6.84%），可能误判要砍线 |
| 3 | **转化后买的是正装还是又一个引流品？** | 如果只是"从一个样品换到另一个样品"，转化率要打折 |
| 4 | **回来的时机集中在第几天？** | 决定二次触达的时点，首周触达往往价值最低 |

---

## 二、核心口径（照抄，不用再想）

| 项 | 口径 |
|:--|:--|
| 自营 | `o.merchant_type = 0`（排除 POP） |
| 有效订单 | `o.eorder_status in ('2','3','7','8','9','10')` |
| 已删除行 | `coalesce(c.delete_flag, '0') = '0'`（商品明细表专属字段） |
| 时间 | 商品明细表**没有支付时间**，必须 join 订单主表取 `o.eorder_pay_time` |
| 快照取数 | 两表都是 `dt = date_sub(current_date(), 1)` 全量快照，**时间靠 eorder_pay_time 卡，不靠 dt** |
| 新客 | `2026-07-01` 之前在该店无有效购买（基线日按分析需求改） |
| 转化 | T0 之后 N 天内、**不含引流品 SKU** 的有效订单 |
| **T0** | 该用户**首次**买该引流品的日期（`min(pay_date)`，一人只算一次） |

**表关系**：
```
dw_dwd.fact_dwd_eord_eorder_commodity_d_his   (商品行粒度，有 esku_code / 无支付时间)
  └─ join dw_dws.dws_eorder_eorder_d_his_combine  on eorder_id  (订单级，有 pay_time / status / merchant_type)
```

---

## 三、SQL 模板（五段，按需取用）

### ① 骨架：新客 + T0（所有分析的地基）

```sql
with params as (
  select 'P04672-000003' as sku_code, '2026-07-01' as new_start
),
sku_all as (
  select c.mem_id, c.eorder_id, date(o.eorder_pay_time) as pay_date
    , coalesce(c.ecmdty_real_pay_money, 0) as real_pay
  from dw_dwd.fact_dwd_eord_eorder_commodity_d_his c
  join dw_dws.dws_eorder_eorder_d_his_combine o
    on c.eorder_id = o.eorder_id and o.dt = date_sub(current_date(), 1)
  cross join params p
  where c.dt = date_sub(current_date(), 1)
    and c.esku_code = p.sku_code
    and coalesce(c.delete_flag, '0') = '0'
    and o.merchant_type = 0
    and o.eorder_status in ('2','3','7','8','9','10')
),
first_trial as (
  select mem_id, min(pay_date) as t0, left(min(pay_date), 7) as ym
  from sku_all group by mem_id
),
pre_buy as (
  select distinct o.mem_id
  from dw_dws.dws_eorder_eorder_d_his_combine o
  join first_trial f on o.mem_id = f.mem_id
  cross join params p
  where o.dt = date_sub(current_date(), 1)
    and o.merchant_type = 0
    and o.eorder_status in ('2','3','7','8','9','10')
    and date(o.eorder_pay_time) < p.new_start
),
new_users as (            -- 真新客；如需限定观察期，在这里加 datediff 条件
  select f.mem_id, f.t0, f.ym
  from first_trial f
  left anti join pre_buy pb on f.mem_id = pb.mem_id
),
trial_orders as (         -- 含引流品的订单，转化时要排除
  select distinct c.eorder_id
  from dw_dwd.fact_dwd_eord_eorder_commodity_d_his c
  cross join params p
  where c.dt = date_sub(current_date(), 1) and c.esku_code = p.sku_code
)
```

### ② 分层：新客 / 沉默回流 / 留存（窗口内买家身份）

见 [[用户分层SQL模板]]，把窗口收敛到目标 SKU 即可。关键：**按 `min(ym)` 去重，一人只进一桶**。

### ③ 三窗口累计转化（评估周期的核心）

```sql
conv_raw as (
  select n.mem_id, n.ym, n.t0
    , datediff(date(o.eorder_pay_time), n.t0) as day_diff
    , coalesce(o.eorder_income, 0) as income
  from dw_dws.dws_eorder_eorder_d_his_combine o
  join new_users n on o.mem_id = n.mem_id
  left anti join trial_orders t on o.eorder_id = t.eorder_id
  where o.dt = date_sub(current_date(), 1)
    and o.merchant_type = 0
    and o.eorder_status in ('2','3','7','8','9','10')
    and date(o.eorder_pay_time) >  n.t0
    and date(o.eorder_pay_time) <= date_add(n.t0, 90)   -- 一次取到最长窗口
),
per_user as (
  select mem_id, ym
    , max(case when day_diff <= 30 then 1 else 0 end) as c30
    , max(case when day_diff <= 60 then 1 else 0 end) as c60
    , min(day_diff) as first_conv_day
    , sum(case when day_diff <= 90 then income else 0 end) as inc90
  from conv_raw group by mem_id, ym
)
-- 外层各窗口的分子分母都必须加 datediff(current_date(), n.t0) >= N 的双重限定
```

**必须同时输出** `满30天 / 满60天 / 满90天` 三个分母，否则新月份会把转化率算低（观察期没到）。

### ④ 双峰时段分布（定触达时点）

```sql
-- 只取观察期已满 90 天的人，按首次转化天数分档
select
  case
    when first_day <= 3  then '1 T0+1~3天'
    when first_day <= 7  then '2 T0+4~7天'
    when first_day <= 15 then '3 T0+8~15天'
    when first_day <= 30 then '4 T0+16~30天'
    when first_day <= 60 then '5 T0+31~60天'
    else                      '6 T0+61~90天'
  end as 转化时段
  , count(*) as 转化人数
  , round(avg(first_day), 1) as 平均天数
from first_conv group by 1
```

### ⑤ 转化后买了什么（验证含金量）

两步：先按**单价档**看结构，再**按人去重**分 A/B/C 三类。

```sql
-- 按人去重（人次 ≠ 人数，这一步不能省）
per_user as (
  select cv.mem_id
    , max(case when c.ecmdty_sale_money >= 15 then 1 else 0 end) as buy_reg
    , max(case when c.ecmdty_sale_money <  15 then 1 else 0 end) as buy_low
    , sum(coalesce(c.ecmdty_real_pay_money, 0)) as amt
  from dw_dwd.fact_dwd_eord_eorder_commodity_d_his c
  join conv_orders cv on c.eorder_id = cv.eorder_id
  where c.dt = date_sub(current_date(), 1)
    and coalesce(c.delete_flag, '0') = '0'
    and c.esku_code <> 'P04672-000003'
  group by cv.mem_id
)
select
  case when buy_reg = 1 and buy_low = 1 then 'A 正装+低价品都买'
       when buy_reg = 1                   then 'B 只买正装'
       else                                    'C 只买低价品（≈未付费）' end as 转化类型
  , count(*) as 人数, round(sum(amt), 2) as 实付金额
from per_user group by 1
```

> ⚠️ 分档用 `ecmdty_sale_money`（销售定价 = 单件标价），**不要用 `ecmdty_payable_money`** —— 后者是行级总价，可能含多件，会把正装误判成高价档。

---

## 四、算经济结论（四步，全用脚本算，别手算）

```
① 引流品毛利 = 收入 − 件数 × 单件成本
   件数 = 实付总额 ÷ 单件实付（明细表无数量字段，只能反推）
② 判断：毛利 ≈ 0 → 获客成本 = 0 → **规模优先于转化率**
③ 每 1,000 新客净得 = 转化人数/千人 × 转化客单价 × 正装毛利率
④ 敏感度：转化率每 +1pp，利润约 +22%
```

**关键判断句**：成本为 0 时，**发 2,000 人（4.5%）= 发 1,000 人（8%）**，规模优先。

---

## 五、四次踩坑（都是实战踩的，写下来防复发）

| # | 坑 | 错误表现 | 正确做法 |
|:-:|:--|:--|:--|
| 1 | **用 30 天当真实转化率** | 算出 4.45%，差点判断"要砍这条线" | 引流品必须看 **90 天**（实测 6.84%，低估 54%）。评估周期写死在模板里 |
| 2 | **CTE 先按月份聚合，外层再过滤老客** | 分子含老客、分母不含 → 转化率虚高（4.7% 算成 6.5%、10 月算成 18.6%） | 把「符合条件的人群」做成**唯一入口 CTE**（如 `new_users`），分子分母都从它派生，绝不在下游再补过滤 |
| 3 | **人次当人数读** | "34.7% 的转化者在买小样"（实际只有 3.3% **只**买小样） | 分档统计后必须**按人去重**分 A/B/C 三类再下结论 |
| 4 | **拿商品明细表当订单表用** | 表里没有 `eorder_pay_time` / `eorder_status` / `merchant_type`，无法卡时间和口径 | 商品明细表只负责 SKU 与金额，**时间/状态/自营一律 join 订单主表**取 |

---

## 六、什么算健康（基线参考）

| 指标 | 参考值 | 说明 |
|:--|:--|:--|
| 90 天转化率 | 5%~10% 常见 | 低于 3% 要查是不是"引流品换引流品" |
| 转化客单价 ÷ 首购人均 | ≥ 3 倍 | 低于 2 倍说明回来的没买正装 |
| 券党（只买低价品）占比 | <10% 可接受 | 超过 20% 转化率要打折 |
| 引流品毛利 | ≈0 最理想 | 净亏就变成"花钱买线索"，要重算 |
| 转化时点 | 双峰：T0+1~3 与 T0+16~30 | 首周触达价值最低，**T0+14 是黄金窗口** |

---

## 七、复用清单（换 SKU 只改三处）

1. `params` 里的 `sku_code`
2. `params` 里的 `new_start`（新客基线日）
3. 分档阈值 `ecmdty_sale_money >= 15`（按该品类低价线调整）

> 关联：[[用户分层SQL模板]] · [[SQL经验库]] · [[AB实验分析SQL模板]] · [[技能库索引]] · [[数据字典索引]]
> 商品明细表字典：[[fact_dwd_eord_eorder_commodity_d_his]] · 订单主表字典：[[dws_eorder_eorder_d_his_combine]]
