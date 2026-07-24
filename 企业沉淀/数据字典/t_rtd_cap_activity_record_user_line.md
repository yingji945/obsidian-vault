---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 一物一码]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_rtd_cap_activity_record_user_line — 活动用户记录行（中奖头表）

**数据库**：`lucky_epromotion`

## 表结构（26 字段）

### 基础标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 |
| 2 | `activity_record_no` | varchar | 活动用户记录行业务编号 |
| 3 | `activity_id` | bigint | 活动 ID |
| 4 | `activity_no` | varchar | 活动编号 |
| 5 | `member_id` | bigint | 会员 ID |
| 6 | `member_name` | varchar | 用户名称快照 |
| 7 | `first_scan_id` | varchar | 首扫码 ID（码占用 unique scan） |

### 奖品信息

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 8 | `prize_row_id` | bigint | 命中奖品行 ID |
| 9 | `prize_name` | varchar | 奖品展示名称快照 |
| 10 | `content_type` | tinyint | 命中奖品内容类型：`1`=红包, `2`=即时券, `3`=咖啡券, `4`=咖啡门店券 |
| 11 | `prize_grant_mode` | varchar | 发放模式快照：`DIRECT`=直接, `PRIVATE_DOMAIN`=私域, `REPURCHASE`=复购 |
| 12 | `expand_option_id` | bigint | 膨胀选项 ID（FR-010 命中 `expand_option.id`） |
| 13 | `city_prize_id` | bigint | 城市奖品矩阵 ID（命中城市概率时有值） |

### 状态 & 履约

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 14 | `record_prize_status` | tinyint | 奖品状态：`1`=待选择, `2`=领取路径, `3`=膨胀路径, `4`=已作废 |
| 15 | `record_coupon_status` | varchar | 汇总活动记录券状态：`10`, `100` 等；待选膨胀阶段可为空 |
| 16 | `fulfillment_phase` | varchar | 履约阶段：`PENDING`=待处理, `EXPAND`=膨胀中, `PENDING_COUPON`=券待发, `PENDING_REDPACK`=红包待发, `WITHDRAW`=已提现, `FULFILLED`=已完成, `VOID`=已作废 |
| 17 | `grant_item_count` | int | grant item 条数 |
| 18 | `fulfillment_fail_code` | varchar | 履约失败码，见 `RtdCapFulfillmentFailCodeEnum`；主动延后（PRIVATE_DOMAIN/REPURCHASE 未触发）不写 |
| 19 | `fulfillment_fail_reason` | varchar | 最近一次履约失败摘要（截断512字符） |
| 20 | `fulfillment_fail_time` | datetime | 最近一次履约失败时间 |
| 21 | `fulfillment_retry_count` | int | 补履约/重试累计失败次数（成功补履约后清零） |

### 其他

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 22 | `location_snapshot` | text | 授权位置摘要 |
| 23 | `member_profile_groups` | varchar | 用户客群 |
| 24 | `claim_time` | datetime | 路径确认时间 |
| 25 | `create_time` | datetime | 创建时间 |
| 26 | `modify_time` | datetime | 修改时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_rtd_cap_participate_log` | `activity_record_no` → `scan_id`（间接） | 扫码参与流水 |
| `t_rtd_cap_activity_prize` | `prize_row_id` → `id` | 奖品行配置 |
| `t_rtd_redpack_user_instance` | `id` → `user_instance_id`（通过 t_rtd_cap_participate_log） | 红包实例 |

## 使用注意点

- **中奖头表**：一条记录代表一次中奖，但中奖≠履约成功，要看 `fulfillment_phase = 'FULFILLED'` 才算真正发奖
- **履约失败重试**：`fulfillment_retry_count` 记录补履约失败次数，成功后会清零
- **`content_type`** 决定奖品形式：红包(`1`)、即时券(`2`)、咖啡券(`3`)、门店券(`4`)，分析不同奖品类型的发放率时按此字段区分
- **`prize_grant_mode`** 决定发放渠道：
  - `DIRECT` = 直接发放（即时到账）
  - `PRIVATE_DOMAIN` = 私域发放（加企微好友领取）
  - `REPURCHASE` = 复购触发（买完再送）
- **膨胀机制**：`expand_option_id` 不为空表示命中了膨胀选项，`record_prize_status = 3` 表示在膨胀路径中
- **`fulfillment_fail_code` 为空不一定成功**：可能正在处理中（`PENDING`），看 `fulfillment_phase` 为准
- **首扫 ID**：`first_scan_id` 是码的唯一标识，"首扫"的含义是同一个码被首次扫码

关联：[[t_rtd_cap_participate_log]] · [[t_rtd_cap_activity_prize]] · [[数据字典索引]]
