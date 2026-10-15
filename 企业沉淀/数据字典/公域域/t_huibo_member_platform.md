---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 公域]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_huibo_member_platform — 慧博会员平台信息表

**数据库**：`lucky_ethirdparty`

## 表结构

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 ID |
| 2 | `third_member_id` | bigint | 外部会员表 ID（关联 `t_third_member.id`） |
| 3 | `first_shop_no` | varchar | 首次入会店铺编码 |
| 4 | `shop_no` | varchar | 已入会店铺编码，多个用逗号拼接 |
| 5 | `platform` | varchar | 平台类型：`TAOBAO`=淘宝, `DOUYIN`=抖音, `JINGDONG`=京东 |
| 6 | `nick` | varchar | 平台昵称 |
| 7 | `platform_member_id` | varchar | 平台侧会员 ID（如淘宝 buyer_id） |
| 8 | `omid` | varchar | 淘宝 omid，仅淘宝时有值 |
| 9 | `mobile` | varchar | 平台级别用户加密手机号码 |
| 10 | `level` | varchar | 淘宝付费等级：`99`=付费会员, `1`=非付费会员。仅淘宝时有值 |
| 11 | `first_shop_time` | datetime | 首次入会店铺时间 |
| 12 | `is_bind` | tinyint | 绑定状态：`0`=解绑, `1`=绑定 |
| 13 | `member_create_time` | datetime | 首次入会时间 |
| 14 | `member_update_time` | datetime | 会员更新时间 |
| 15 | `create_user_id` | varchar | 创建人 |
| 16 | `create_username` | varchar | 创建人名称 |
| 17 | `create_time` | datetime | 创建时间 |
| 18 | `update_user_id` | varchar | 修改人 |
| 19 | `update_username` | varchar | 修改人名称 |
| 20 | `update_time` | datetime | 更新时间 |
| 21 | `is_encrypted` | tinyint | 是否加密：`0`=未加密, `1`=已加密 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_third_member` | `third_member_id` → `id` | 外部会员（一对多：一个会员可绑定多个平台） |
| `t_third_parent_order` | `platform_member_id` → `platform_member_id` | 第三方订单（同一个平台账号的订单） |

## 使用注意点

- **`platform` 是分析时的关键入口**：限定 `TAOBAO` 才能拿到准确的淘宝端数据
- **`is_bind = 1`**：只取已绑定的记录，解绑的记录不应计入当前用户
- **`omid`** 和 **`level`** 仅淘宝平台有值，其他平台为空
- **`shop_no`**：逗号拼接多店铺，必要时用 `FIND_IN_SET` 或 `SPLIT` 处理
- **`third_member_id` 一对多**：一个 `t_third_member` 可能关联多个平台记录（如同时有淘宝和抖音）

## 典型 SQL

```sql
-- 查找某平台有效绑定的用户
select tm.member_no, hmp.platform_member_id, hmp.nick
from lucky_ethirdparty.t_third_member tm
inner join lucky_ethirdparty.t_huibo_member_platform hmp
  on tm.id = hmp.third_member_id
 and hmp.platform = 'TAOBAO'
 and hmp.is_bind = 1
where tm.member_no <> '';
```

关联：[[t_third_member]] · [[t_third_parent_order]] · [[数据字典索引]]
