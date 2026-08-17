---
created: 2026-07-28
updated: 2026-07-28
tags: [SQL, 用户分层, 技能库, 数据分析]
---

# 用户分层 SQL 模板（新客/留存/沉默）

> 适用场景：给定分析窗口（Q1/H1/全年），将窗口内有消费的用户分为三类：
> - **新客**：首单在窗口内
> - **留存**：上一年也有消费
> - **沉默**：上一年没消费，但历史上消费过（回流）
> - 兜底：历史都无记录 → 保守归新客

## 最终 SQL

```sql
with
t1 as -- 全量有效订单
(
select
date(eorder_pay_time) as pay_date,
left(date(eorder_pay_time),7) as ym,
left(date(eorder_pay_time),4) as yy,
mem_id,
eorder_id as oid,
sum(eorder_income) as income
from dw_dws.dws_eorder_eorder_d_his_combine
where dt = date_sub(current_date(), 1)  -- 最新全量分区
  and date(eorder_pay_time) <= '2026-06-30'  -- ← 分析窗口截止时间，改这里即可
  and total_ecmdty_payable_money <> 0
  and eorder_status in ('2','3','7','8','9','10')
group by 1,2,3,4,5
),
t_first_order as -- 每个会员首次支付日期
(
select mem_id, min(pay_date) as first_dt
from t1 group by mem_id
),
user_2025 as (select distinct mem_id from t1 where yy = '2025'),
user_2026 as (select distinct mem_id from t1 where yy = '2026'),
user_history as (select distinct mem_id from t1 where yy < '2025')
select
case
  when tn.first_dt is not null and left(tn.first_dt,4) = '2026' then '新客'
  when b.mem_id is not null then '留存'
  when h.mem_id is not null then '沉默'
  else '新客'
end as user_type,
count(distinct a.mem_id) as user_cnt,
count(distinct o.oid) as order_cnt,
sum(o.income) as income
from user_2026 a
left join user_2025 b on a.mem_id = b.mem_id
left join user_history h on a.mem_id = h.mem_id
left join t_first_order tn on a.mem_id = tn.mem_id
left join t1 o on a.mem_id = o.mem_id and o.yy = '2026'
group by 1
;
```

## 切换分析窗口

只改 `t1` 里的截止时间，所有下游 CTE 自动对齐：

| 窗口 | 截止条件 |
|:----|:--------|
| 2026 Q1 | `and date(eorder_pay_time) <= '2026-03-31'` |
| 2026 H1 | `and date(eorder_pay_time) <= '2026-06-30'` |
| 2026 全年 | `and date(eorder_pay_time) <= '2026-12-31'` |

> ⚠️ 不能在 `t1` 加下限（如 `>= '2024-01-01'`），因为 `dws_eorder_eorder_d_his_combine` 是全量快照表，`dt = date_sub(current_date(), 1)` 已经包含所有历史数据。下限会丢失沉默用户的早期记录。

## 分类逻辑

```
2026年窗口内有消费的用户
├── 且首单在2026年 → 新客
├── 且2025年也有消费 → 留存
├── 且2025年没消费，但2024年或更早有消费 → 沉默
└── 历史都无记录（理论上不会发生） → 保守归新客
```

## 命名说明

- 本模板中的"**沉默**"= 旧版 SQL 中的"**回流**"，同一个概念的不同命名。
- 命名为"沉默"的理由：沉默用户 = 流失后又回来的用户，强调"中间断了一年的沉默期"。
- 兜底归"新客"而非"未知"：数据完整性无法100%保证时，保守原则向新客倾斜。

## 前置条件

- `dws_eorder_eorder_d_his_combine` 是**全量快照表**，一个分区包含所有历史订单
- `eorder_status in ('2','3','7','8','9','10')` = 有效订单
- `total_ecmdty_payable_money <> 0` = 剔除门店兑换单（临时策略，与线上模型对齐）

## 经验教训（from 2026-07-28 coding review）

本次 SQL 编写走了弯路，根源在于**没确认数据模型就下笔**：

| 问题 | 正确做法 |
|:----|:--------|
| 默认加了 `>= '2024'` 下限 | 先问：全量快照还是增量？全量不需要下限 |
| 在多个 CTE 级联改参数 | 找单一控制点——所有数据从 `t1` 出，改 `t1` 一处即可 |
| 用户说加窗口支持，我复杂化 | 先给出最简单的方案，等用户说不够再加 |

**核心原则：**
1. 写 SQL 前先画数据流，找到单一控制点
2. 先确认表模型（全量/增量/拉链）再动手
3. 从最简单的方案开始，不要提前复杂化

## 设计决策记录
| 分析窗口控制方式 | 在 `t1` 加 `date(eorder_pay_time) <= <截止>` | 一改全改，所有 CTE 口径自动对齐，不会出现"判断新客用的首单日期比分析窗口还大"的不一致 |
| 历史回溯范围 | 不设下限，利用全量快照 | 全量快照表无需手动回溯，否则会丢失历史数据 |
| 沉默用户判断 | 用 `user_history` (yy < '2025') 而非只到2024 | 沉默用户可能在更早年有消费，需要全量历史 |
