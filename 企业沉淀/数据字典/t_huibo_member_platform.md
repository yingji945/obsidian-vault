---
created: 2026-07-24
tags: [企业, 数据, 字典, 公域]
field_status: 待补充
---

# t_huibo_member_platform — 第三方会员平台绑定

**数据库**：`lucky_ethirdparty`

> ⚠️ **字段待补充**

## 已知字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `id` | bigint | 主键 |
| `third_member_id` | bigint | 关联 `t_third_member.id` |
| `platform_member_id` | varchar | 平台侧用户 ID（如淘宝的 buyer_id） |
| `platform` | varchar | 平台标识：`TAOBAO`=淘宝, `TMALL`=天猫 等 |
| `is_bind` | tinyint | 是否绑定：`0`=否, `1`=是 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_third_member` | `third_member_id` → `id` | 第三方会员 |
| `t_third_parent_order` | `platform_member_id` → `platform_member_id` | 第三方订单 |

关联：[[t_third_member]] · [[t_third_parent_order]] · [[数据字典索引]]
