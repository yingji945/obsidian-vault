---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 公域]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_third_member — 外部会员表

**数据库**：`lucky_ethirdparty`

## 表结构

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 ID |
| 2 | `mobile` | varchar | 加密手机号码 |
| 3 | `member_no` | varchar | 咖啡侧会员编号 |
| 4 | `original_member_id` | varchar | 数据源侧会员 ID |
| 5 | `name` | varchar | 姓名 |
| 6 | `sex` | varchar | 性别 |
| 7 | `birthday` | datetime | 生日 |
| 8 | `province` | varchar | 省 |
| 9 | `city` | varchar | 市 |
| 10 | `district` | varchar | 区 |
| 11 | `email` | varchar | 邮箱 |
| 12 | `address` | varchar | 详细地址 |
| 13 | `member_points` | decimal | 积分余额 |
| 14 | `level` | varchar | 等级 |
| 15 | `external_origin` | varchar | 数据源（如 TAOBAO 等） |
| 16 | `member_create_time` | datetime | 首次入会时间 |
| 17 | `member_update_time` | datetime | 会员更新时间 |
| 18 | `create_user_id` | varchar | 创建人 |
| 19 | `create_username` | varchar | 创建人名称 |
| 20 | `create_time` | datetime | 创建时间 |
| 21 | `update_user_id` | varchar | 修改人 |
| 22 | `update_username` | varchar | 修改人名称 |
| 23 | `update_time` | datetime | 更新时间 |
| 24 | `order_synced` | tinyint | 咖啡订单是否已同步到数据源侧：`0`=未同步, `1`=已同步 |
| 25 | `is_encrypted` | tinyint | 是否加密：`0`=未加密, `1`=已加密 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_huibo_member_platform` | `id` → `third_member_id` | 平台绑定（一对多） |
| `t_member` | `member_no` → `member_no` | 咖啡侧会员（匹配） |

## 使用注意点

- **`member_no` 不能为空**：过滤 `member_no <> ''`，否则 join t_member 会出脏数据
- **`external_origin`**：数据源标记，区分不同第三方平台
- **`mobile`**：已加密，不能直接原文匹配
- **`is_encrypted`**：标记敏感字段是否已加密处理
- **`member_create_time`**：会员在第三方平台的首次入会时间，不等同于咖啡侧 `t_member` 的注册时间

关联：[[t_huibo_member_platform]] · [[t_third_parent_order]] · [[数据字典索引]]
