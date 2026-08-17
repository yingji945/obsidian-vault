---
created: 2026-07-24
tags: [企业, 数据, 字典, 企微]
source: 用户提供 @ 2026-07-24
---

# t_wecom_external_user — 企微客户现状

**数据库**：`lucky_wecom`

## 表结构

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `id` | bigint | 自增主键 |
| `user_id` | varchar | 服务人员的 user id |
| `external_user_id` | varchar | 外部联系人 userid |
| `external_user_name` | varchar | 外部联系人名称 |
| `wx_unionid` | varchar | 微信 unionid |
| `deleted_user_time` | datetime | 删除服务人员时间 |
| `added_user_time` | datetime | 添加服务人员时间 |
| `status` | tinyint | 状态：`0`=无效，`1`=有效 |
| `brand_type` | varchar | 品牌类型：`LK001`=luckin coffee, `LK002`=小鹿茶 |
| `created_time` | datetime | 创建时间 |
| `modified_time` | datetime | 修改时间 |
| `is_one_way_friend` | tinyint | 单向好友关系：`0`=否，`1`=是 |
| `user_type` | varchar | 用户类型：`wechat`=微信用户，`wecom`=企业微信用户 |
| `relation_type` | varchar | 关系类型：`add_external_contact`=互为好友，`del_external_contact`=员工侧删除，`del_follow_user`=客户侧删除，`both_del`=互相删除 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_wecom_external_user_history` | `external_user_id` | 企业微信客户事件流水 |

## 使用注意点

- **现状表**：同一个人**只有一条记录**，反映当前关系状态（区别于流水表）
- **`status`**：只查 `status = 1`（有效）
- **`relation_type`** 决定了员工和客户之间的当前关系状态：
  - `add_external_contact` = 正常好友关系
  - `del_external_contact` = 员工把客户删了
  - `del_follow_user` = 客户把员工删了
  - `both_del` = 互相删了
- **`is_one_way_friend`** = 1 表示单向好友（仅客户单向添加员工），渠道来源不明
- **`added_user_time`** 是首次加好友时间，类似 `t_wecom_external_user_history` 中的 `event_time`

## 典型 SQL

```sql
-- 当前企微好友总数（有效且互为好友）
select count(distinct wx_unionid) as friend_cnt
from lucky_wecom.t_wecom_external_user
where status = 1
  and relation_type = 'add_external_contact'
  and is_one_way_friend = 0
  and wx_unionid is not null;

-- 某渠道在有效期内的留存好友
select
  count(distinct u.wx_unionid) as friend_cnt,
  count(distinct case when u.member_id is not null then u.member_id end) as member_cnt
from lucky_wecom.t_wecom_external_user u
where u.status = 1
  and u.added_user_time >= '2026-07-08'
  and u.added_user_time < '2026-07-09'
  and u.wx_unionid is not null;
```

关联：[[t_wecom_external_user_history]] · [[数据字典索引]]
