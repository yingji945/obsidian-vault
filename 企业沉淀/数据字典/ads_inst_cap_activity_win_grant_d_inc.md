---
created: 2026-07-29
tags: [企业, 数据, 字典, 一物一码, 瓶内营销]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-29
---

# ads_inst_cap_activity_win_grant_d_inc — 瓶盖扫码活动参与及中奖宽表

**数据库**：`dw_ads`

> 一物一码项目核心 ADS 表，覆盖从参与→中奖→膨胀→履约全链路。

## 关联键

| 关联字段 | 关联表 | 说明 |
|:--------|:------|:----|
| `activity_id` / `activity_no` | [[dim_inst_rtd_cap_activity_d_his]] | 活动维表 |

## 使用注意点

- 一物一码项目的**核心宽表**，写分析 SQL 优先从这查
- `participate_time` 适合做时间筛选，`win_time` 可能滞后
- `fulfillment_fail_code` 不为空表示履约失败，需要关注
- `is_expand = 1` 表示用户选择了膨胀，膨胀后的奖品在 `expand_prize_name`

## 表结构（39 字段）

### 参与标识

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 1 | `participate_id` | 活动参与记录 ID |
| 2 | `participate_time` | 参与时间 |
| 3 | `activity_id` | 活动 ID |
| 4 | `activity_no` | 活动编号 |
| 5 | `activity_name` | 活动名称 |
| 6 | `mem_id` | 会员 ID |
| 7 | `scan_id` | 扫码 ID |
| 8 | `participate_phase` | 参与阶段 |
| 9 | `layer_break_code` | 拦截层诊断码 |
| 10 | `hit_result` | 命中结果 |

### 中奖信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 11 | `record_id` | 用户中奖记录 ID |
| 12 | `activity_record_no` | 活动记录编号 |
| 13 | `win_time` | 中奖时间 |
| 14 | `claim_time` | 路径确认时间 |
| 15 | `prize_row_id` | 命中基础奖品行 ID |
| 16 | `prize_name` | 奖品名称 |
| 17 | `base_content_type` | 基础内容类型 |
| 18 | `base_grant_mode` | 基础获得方式 |
| 19 | `base_grant_mode_snap` | 基础获得方式快照 |

### 膨胀信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 20 | `is_expand_support` | 是否支持膨胀 |
| 21 | `expand_option_id` | 膨胀选项 ID |
| 22 | `exp_prize_row_id` | 膨胀对应奖品行 ID |
| 23 | `is_expand` | 是否膨胀获得 |
| 24 | `expand_prize_name` | 膨胀奖品名称 |
| 25 | `expand_target_type` | 膨胀目标类型 |
| 26 | `expand_grant_mode` | 膨胀获得方式 |
| 27 | `final_grant_mode` | 最终获得方式 |

### 履约信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 28 | `fulfillment_phase` | 履约阶段 |
| 29 | `grant_item_cnt_snap` | 发放明细数量快照 |
| 30 | `grant_item_cnt` | 实际发放明细数量 |
| 31 | `redpack_grant_cnt` | 红包发放数量 |
| 32 | `inst_coupon_grant_cnt` | 即时券发放数量 |
| 33 | `cfcoupon_grant_cnt` | 咖啡库券发放数量 |
| 34 | `coffee_store_coupon_grant_cnt` | 咖啡店券发放数量 |
| 35 | `first_grant_time` | 首次发放时间 |
| 36 | `last_grant_time` | 最后发放时间 |

### 转账信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 37 | `redpack_instance_cnt` | 红包实例数量 |
| 38 | `redpack_transferred_cnt` | 红包已转账数量 |
| 39 | `redpack_not_transferred_cnt` | 红包未转账数量 |
| 40 | `redpack_transferred_amt` | 红包已转账金额 |
| 41 | `last_transfer_done_time` | 最后转账完成时间 |

### 失败信息

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 42 | `fulfillment_fail_code` | 履约失败码 |
| 43 | `fulfillment_fail_reason` | 履约失败原因 |
| 44 | `fulfillment_fail_time` | 履约失败时间 |
| 45 | `fulfillment_retry_cnt` | 履约重试次数 |

## 典型 SQL

```sql
-- 按活动统计：参与人数、中奖人数、膨胀率、履约率
SELECT
  activity_no,
  activity_name,
  COUNT(DISTINCT mem_id) AS participate_users,
  COUNT(DISTINCT CASE WHEN record_id IS NOT NULL THEN mem_id END) AS win_users,
  COUNT(DISTINCT CASE WHEN is_expand = 1 THEN mem_id END) AS expand_users,
  COUNT(DISTINCT CASE WHEN fulfillment_phase = 'done' THEN mem_id END) AS fulfilled_users
FROM dw_ads.ads_inst_cap_activity_win_grant_d_inc
WHERE participate_time >= '2026-08-01'
  AND participate_time <  '2026-09-01'
GROUP BY activity_no, activity_name;
```

## 关联表

- [[dim_inst_rtd_cap_activity_d_his]] — 活动维表（通过 activity_id/activity_no 关联）
