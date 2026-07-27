---
created: 2026-07-21T18:40:00+08:00
tags:
  - 知识沉淀
  - SQL
  - 数据分析
  - 运营分析
  - 技能参考
source: 对应 skill: ops-data-analytics（Hermes 自动加载的数据分析流程）
see_also:
  - 对应的 skill 本体不在 vault 内，本文件是 vault 可读版
  - 个人成长/SQL经验库.md
references:
  - 个人成长/SQL经验库.md
  - 业务分析/运营数据分析方法论.md
---

# 运营数据分析 — SQL 模式与框架参考

> 对应 skill: `ops-data-analytics`。Hermes 做数据分析时自动加载的完整 SQL 模式库。

---

## 一、常用表

### 订单表（核心）

`dw_dws.dws_eorder_eorder_d_his_combine`
- 分区：`dt`
- 过滤条件：`total_ecmdty_payable_money <> 0`, `eorder_status IN (2,3,7,8,9,10)`
- 关键字段：`mem_id`, `eorder_pay_time`, `eorder_income`, `eorder_status`
- `merchant_type`: 0自营, 1代销, 2POP
- `sales_model`: 1普通, 2众筹, 3预售
- `eorder_type`: 1电商, 2卡券, 3供应商
- `payment_status`: 10待付, 20部分, 30已付

### 事件追踪表

`ods_log.t_hmonitor_track_event` → 用户行为（页面浏览、点击、自定义事件）
`dw_dwd.fact_dwd_log_c_start_retention_detail_d_inc` → App启动/留存明细
`dw_dwd.fact_dwd_log_c_luckinpop_detail_d_inc` → 电商分析（event_code, prop_data JSON扩展）

### 实验表

`dw_dim.dim_con_test_template_d_his` → AB实验模板维度

### RTD 扫码活动表

`lucky_epromotion.t_rtd_cap_participate_log` 扫码参与
`lucky_epromotion.t_rtd_cap_activity_record_user_line` 中奖头表
`lucky_epromotion.t_rtd_cap_activity_prize` 奖品行配置
`lucky_epromotion.t_rtd_redpack_user_instance` 红包实例

---

## 二、核心 SQL 模式

### 2.1 用户生命周期分群

```sql
新客：首单落在本周期内
留存：过去3个月内有订单
回流：有历史订单但过去3个月无订单
```

### 2.2 曝光→点击→下单漏斗（session级归因）

关键改进：用 `session_id` 替代宽松的 `member_id + date` 匹配，减少跨活动污染。

注意：`session_id` 只存在于前端事件表，后端订单表没有它。曝光→点击可以精确归因，点击→下单仍需依赖 member_id + 时间窗口。

### 2.3 渠道→商城→下单漏斗（同天）

```sql
自然流量 app_start → 进入即享商城页面 → 同天下单
```

### 2.4 RTD 扫码复购分析

常用指标：扫码人数/次数、中奖人数、选择膨胀人数、红包费用

---

## 三、Spark SQL 注意事项

| 不要用 | 用这个 | 原因 |
|---|---|---|
| `now()` | `current_date()` | Spark无 now() |
| `DATEDIFF(month, b, a)` | `months_between(b, a)` | DATEDIFF只返回天数 |
| `BETWEEN` 做时间过滤 | `>= AND <`（半开区间） | 用户偏好 |

### 性能优化

- JSON条件+大量event_code的 OR 查询 → 拆成 UNION ALL（否则谓词下推失效）
- 小表 join 大表 → 加 `/*+ broadcast(小表) */`
- LIKE 如果字段总以同一前缀开头 → 去掉前导 `%` 启用前缀匹配

---

## 四、常见陷阱

1. **NULL NOT IN** — `col NOT IN ('a','b')` 在 col=NULL 时不返回任何行。用 `(col IS NULL OR col NOT IN (...))`。
2. **datediff 的 NULL** — LEFT JOIN 模式下 datediff(NULL, a.date) 返回 NULL。用 `coalesce(datediff(...), 999)` 推出范围。
3. **LEFT JOIN 链中的日期丢失** — t_mall LEFT JOIN t_order ON user_id 不加 date 条件会导致订单被 N 倍放大。必须同时 join user_id 和 date。
4. **ORDER 子查询中的分区硬编码** — 最常出现的 bug。事件表和订单表 join 时，订单表 `dt` 必须用日期范围变量而非 `date_sub(current_date(),1)`。

---

*对应 skill: `ops-data-analytics`（含完整 SQL 模板和参考文件）*
