---
created: 2026-07-24
tags: [企业, 数据, 字典, 企微]
source: 用户提供 @ 2026-07-24
---

# t_wecom_external_user_history — 企微客户事件流水

**数据库**：`lucky_wecom`

## 表结构

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `id` | bigint | 自增主键 |
| `user_id` | varchar | 服务人员的 user id |
| `member_id` | varchar | 用户 id |
| `user_name` | varchar | 服务人员名称 |
| `external_user_id` | varchar | 外部联系人 userid |
| `external_user_name` | varchar | 外部联系人名称 |
| `wx_unionid` | varchar | 微信 unionid |
| `event_type` | varchar | 事件的类型（加好友/删好友等） |
| `event_time` | datetime | 事件发生时间 |
| `state` | varchar | 加好友的渠道（如"电商资源-电商弹窗-1分钱杯子"） |
| `brand_type` | varchar | 品牌类型：`LK001`=luckin coffee, `LK002`=小鹿茶 |
| `created_time` | datetime | 创建时间 |
| `modified_time` | datetime | 修改时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_wecom_external_user` | `external_user_id` | 企微客户现状（同一个外部联系人） |

## 使用注意点

- **流水表**：每条记录是**一个事件**（加好友/删好友/改备注等），同一个人可能有多次记录
- **`state` 渠道码**：用来区分不同获客来源，如 `'电商资源-电商弹窗-1分钱杯子'`、`'投放-朋友圈广告'` 等
- **`wx_unionid`**：微信全域唯一标识，跨公众号/小程序/企业微信的统一 ID
- **`event_type`** 常见值：联系时为 `add_external_contact`（互为好友），删除时可能是 `del_external_contact`（员工侧删除）或 `del_follow_user`（客户侧删除）
- **取人数时注意**：按 `wx_unionid` 去重获得微信用户数，按 `member_id` 去重获得瑞幸会员数（`member_id` 为空表示非会员）

## 典型 SQL

```sql
-- 统计某渠道某天添加的微信用户数和会员数
select
  count(distinct t.wx_unionid) as wx_user_cnt,
  count(distinct case when t.member_id is not null then t.member_id end) as member_cnt
from lucky_wecom.t_wecom_external_user_history t
where t.state = '电商资源-电商弹窗-1分钱杯子'
  and t.event_type = 'add_external_contact'
  and t.event_time >= '2026-07-08'
  and t.event_time < '2026-07-09'
  and t.wx_unionid is not null
  and t.wx_unionid <> '';
```

关联：[[t_wecom_external_user]] · [[数据字典索引]]
