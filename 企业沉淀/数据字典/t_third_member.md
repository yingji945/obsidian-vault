---
created: 2026-07-24
tags: [企业, 数据, 字典, 公域]
field_status: 待补充
---

# t_third_member — 第三方会员基础信息

**数据库**：`lucky_ethirdparty`

> ⚠️ **字段待补充**

## 已知字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `id` | bigint | 主键 |
| `member_no` | varchar | 会员编号（关联咖啡侧会员） |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_huibo_member_platform` | `id` → `third_member_id` | 平台绑定表 |
| `t_member` | `member_no` → `member_no` | 咖啡侧会员 |

## 使用注意点

- 不要用 `member_no = ''` 的用户（脏数据）

关联：[[t_huibo_member_platform]] · [[t_third_parent_order]] · [[数据字典索引]]
