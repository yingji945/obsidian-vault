---
created: 2026-07-24
tags: [企业, 数据, 字典, 一物一码]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_rtd_cap_activity_prize_expand_option — 奖品膨胀选项（二期 1:N）

**数据库**：`lucky_epromotion`

## 表结构（15 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 |
| 2 | `prize_row_id` | bigint | 奖品行 ID（关联 `t_rtd_cap_activity_prize.id`） |
| 3 | `line_sort` | int | 排序（1~N） |
| 4 | `expand_prize_name` | varchar | 膨胀奖品展示名 |
| 5 | `expand_prize_image_url` | varchar | 膨胀奖品大图 HTTPS URL |
| 6 | `expand_proposal_no` | varchar | 膨胀方案编号 |
| 7 | `expand_proposal_id` | bigint | 膨胀方案 ID（冗余） |
| 8 | `expand_target_type` | varchar | 四档内容类型码 |
| 9 | `expand_probability_limit` | tinyint | 膨胀概率限制：`0`=不限, `1`=限定 |
| 10 | `expand_probability` | decimal | 膨胀概率百分数（0~100，`expand_probability_limit=1` 时有效） |
| 11 | `expand_grant_qty` | int | 膨胀路径每模板发放数量 |
| 12 | `prize_expand_mode` | varchar | 膨胀路径发放方式：`DIRECT`, `PRIVATE_DOMAIN`, `REPURCHASE` |
| 13 | `expand_private_domain_channel_qr_code_url` | varchar | 膨胀路径加私域渠道码 HTTPS URL（`prize_expand_mode=PRIVATE_DOMAIN` 时必填） |
| 14 | `create_time` | datetime | 创建时间 |
| 15 | `modify_time` | datetime | 修改时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_rtd_cap_activity_prize` | `prize_row_id` → `id` | 关联的奖品行（一对多：一个奖品可对应多个膨胀选项） |

## 使用注意点

- **二期功能**：膨胀选项是奖品膨胀机制的配置表，`t_rtd_cap_activity_prize.is_expand=1` 的奖品行会有一到多条膨胀选项
- **`line_sort`** 决定膨胀选项的展示顺序，值越小越靠前
- **`expand_probability`** 是膨胀选项自身的命中概率，和 `t_rtd_cap_activity_prize` 的中奖概率是两套独立体系
- **发放模式**：`prize_expand_mode` 和 `t_rtd_cap_activity_prize.prize_grant_mode` 的逻辑一致，但是独立配置（基础路径和膨胀路径可以不同）
- 中奖记录中 `t_rtd_cap_activity_record_user_line.expand_option_id` 指向这张表的 `id`

关联：[[t_rtd_cap_activity_prize]] · [[t_rtd_cap_activity_record_user_line]] · [[数据字典索引]]
