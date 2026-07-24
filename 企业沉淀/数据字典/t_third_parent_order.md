---
created: 2026-07-24
tags: [企业, 数据, 字典, 公域]
field_status: 待补充
---

# t_third_parent_order — 第三方父订单

**数据库**：`lucky_ethirdparty`

> ⚠️ **字段待补充**

## 已知字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `id` | bigint | 主键 |
| `platform_member_id` | varchar | 平台侧用户 ID（关联 `t_huibo_member_platform.platform_member_id`） |
| `platform` | varchar | 平台标识 |
| `status` | varchar | 订单状态：`WAIT_SELLER_SEND_GOODS`=待发货, `WAIT_BUYER_CONFIRM_GOODS`=待收货, `TRADE_BUYER_SIGNED`=已签收, `TRADE_FINISHED`=已完成 |
| `payment` | decimal | 支付金额 |
| `create_time` | datetime | 订单创建时间 |
| `pay_time` | datetime | 支付时间 |
| `finish_time` | datetime | 完成时间 |
| `shop_no` | varchar | 店铺编号 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_huibo_member_platform` | `platform_member_id` → `platform_member_id` | 平台绑定 |
| `t_third_member` | 通过 `t_huibo_member_platform` 间接关联 | 第三方会员 |

## 使用注意点

- `status` 只取 `('WAIT_SELLER_SEND_GOODS', 'WAIT_BUYER_CONFIRM_GOODS', 'TRADE_BUYER_SIGNED', 'TRADE_FINISHED')` 为有效订单
- `platform` 与 `t_huibo_member_platform.platform` 相同（如 `'TAOBAO'`），join 时建议两边都限制
- 公域→私域分析时通过 `platform_member_id` 关联，再通过 `t_third_member.member_no` 桥接到咖啡侧 `t_member`

关联：[[t_third_member]] · [[t_huibo_member_platform]] · [[数据字典索引]]
