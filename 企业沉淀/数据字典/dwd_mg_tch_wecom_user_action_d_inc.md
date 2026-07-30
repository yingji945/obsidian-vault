---
created: 2026-07-29
tags: [企业, 数据, 字典, 企业微信]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-29
---

# dwd_mg_tch_wecom_user_action_d_inc — 企微加好友明细

**数据库**：`dw_dwd`

> 社群-加好友明细记录，lucky/luna（企业微信客户历史）

## 关联键

| 关联字段 | 关联表 | 说明 |
|:--------|:------|:----|
| `mem_id` | 电商订单/用户表 | 可关联用户消费行为 |
| `wx_unionid` | 用户统一身份表 | 微信统一身份 |

## 使用注意点

- `event_type` 区分不同的好友事件类型（加好友/删好友等）
- `state` 记录加好友渠道，做渠道效果分析时关注
- `brand_type` = LK001 瑞幸咖啡 / LK002 小鹿茶，多品牌运营时注意区分

## 表结构（13 字段）

| # | 字段名 | 说明 |
|:-:|:------|:----|
| 1 | `id` | 自增主键 |
| 2 | `lucky_user_id` | 服务人员的 user id |
| 3 | `mem_id` | 用户 id |
| 4 | `lucky_user_name` | 服务人员名称 |
| 5 | `external_user_id` | 外部联系人 userid |
| 6 | `external_user_name` | 外部联系人名称 |
| 7 | `wx_unionid` | 微信 unionid |
| 8 | `event_type` | 事件的类型 |
| 9 | `event_time` | 时间发生时间 |
| 10 | `state` | 加好友的渠道 |
| 11 | `brand_type` | 品牌类型：LK001 luckin coffee / LK002 小鹿茶 |
| 12 | `created_time` | 创建时间 |
| 13 | `modified_time` | 修改时间 |
