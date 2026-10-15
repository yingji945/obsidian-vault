---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 一物一码]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_rtd_cap_participate_log — 扫码参与流水表

**数据库**：`lucky_epromotion`

## 表结构（10 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 |
| 2 | `member_id` | bigint | 会员 ID |
| 3 | `activity_id` | bigint | 活动 ID |
| 4 | `activity_type` | varchar | 活动类型：取值见 `EorderActivityTypeConstants`，如 `RTD CAP REPURCHASE`（瓶盖复购） |
| 5 | `scan_id` | varchar | 扫码 ID（首扫/复扫） |
| 6 | `participate_phase` | tinyint | 阶段：`1`=首扫, `2`=复扫 |
| 7 | `layer_break_code` | varchar | 拦截层诊断码：未拦截为空，码表见 `RtdCapLotteryLayerBreakCodeEnum` |
| 8 | `hit_result` | tinyint | 结果：`0`=未中奖, `1`=中奖 |
| 9 | `user_instance_id` | bigint | 关联 `t_rtd_redpack_user_instance` |
| 10 | `ext_info` | text | 扩展 JSON（可含三方响应摘要、全量 traceId 等） |
| 11 | `create_time` | datetime | 创建时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_rtd_cap_activity_record_user_line` | 通过 `activity_id` + `member_id` | 中奖记录明细 |
| `t_rtd_cap_activity_prize` | `activity_id` → `activity_id` | 活动奖品配置 |

## 使用注意点

- **首扫 vs 复扫**：`participate_phase = 1` 首次扫码，`= 2` 复扫（二次扫码）。分析时按需区分
- **拦截码**：`layer_break_code` 为空表示未被拦截，有值表示在某层被拦截（如风控、频率限制等），码表见 `RtdCapLotteryLayerBreakCodeEnum`
- **`activity_type`**：瓶盖复购类活动标记为 `RTD CAP REPURCHASE`
- **`ext_info` 是 JSON**：可含三方响应摘要、全量 traceId 等信息，需要时解析
- **`hit_result = 1`** 表示中奖，但不是所有中奖都能成功发放（需看关联表确认发放状态）
- **流水表**：同一个人扫同一个码可能有多条记录（首扫+复扫），分析人数时注意去重

关联：[[t_rtd_cap_activity_record_user_line]] · [[t_rtd_cap_activity_prize]] · [[数据字典索引]]
