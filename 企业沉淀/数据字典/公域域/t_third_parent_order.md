---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 公域]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# t_third_parent_order — 父订单信息表

**数据库**：`lucky_ethirdparty`

## 表结构

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `id` | bigint | 主键 ID |
| 2 | `platform_member_id` | varchar | 平台侧会员 ID（关联 `t_huibo_member_platform.platform_member_id`） |
| 3 | `platform` | varchar | 平台类型：`TAOBAO`=淘宝, `DOUYIN`=抖音, `JINGDONG`=京东 |
| 4 | `shop_no` | varchar | 店铺编码 |
| 5 | `nick` | varchar | 平台昵称 |
| 6 | `platform_parent_order_id` | varchar | 平台订单编号 |
| 7 | `payment` | decimal | 订单金额（单位：元） |
| 8 | `status` | varchar | 订单状态 |
| 9 | `type` | varchar | 交易类型 |
| 10 | `include_postage` | varchar | 是否包含邮费 |
| 11 | `postage` | decimal | 邮费（单位：元） |
| 12 | `step_paid_fee` | decimal | 分阶段付款的已付金额（单位：元） |
| 13 | `step_trade_status` | varchar | 分阶段付款的订单状态 |
| 14 | `external_origin` | varchar | 数据源 |
| 15 | `pay_time` | datetime | 支付时间 |
| 16 | `finish_time` | datetime | 完成时间 |
| 17 | `order_create_time` | datetime | 订单下单时间 |
| 18 | `order_update_time` | datetime | 订单更新时间 |
| 19 | `create_user_id` | varchar | 创建人 |
| 20 | `create_username` | varchar | 创建人名称 |
| 21 | `create_time` | datetime | 创建时间 |
| 22 | `update_user_id` | varchar | 修改人 |
| 23 | `update_username` | varchar | 修改人名称 |
| 24 | `update_time` | datetime | 更新时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_huibo_member_platform` | `platform_member_id` → `platform_member_id` | 平台绑定（同一个平台账号的订单） |
| `t_third_member` | 通过 `t_huibo_member_platform` 间接 | 外部会员 |

## 使用注意点

- **有效订单状态**：`status IN ('WAIT_SELLER_SEND_GOODS', 'WAIT_BUYER_CONFIRM_GOODS', 'TRADE_BUYER_SIGNED', 'TRADE_FINISHED')`
- **平台一致性**：join `t_huibo_member_platform` 时 `platform` 两边都要限制（如 `= 'TAOBAO'`），否则会跨平台匹配到错误的用户
- **字段对比**：注意 `order_create_time`（下单时间）、`pay_time`（支付时间）、`finish_time`（完成时间）三个时间戳有区别，分析时按需选用
- **公域→私域分析链路**：`t_third_parent_order.platform_member_id` → `t_huibo_member_platform.platform_member_id` → `t_huibo_member_platform.third_member_id` → `t_third_member.id` → `t_third_member.member_no` → `t_member.member_no`
- **`payment` 单位是元**，不比 `dws_eorder_eorder_d_his_combine` 的金额单位，注意统一口径

## 典型 SQL

```sql
-- 某平台某段时间的有效订单金额汇总
select
  count(distinct tpo.platform_parent_order_id) as order_cnt,
  count(distinct tpo.platform_member_id) as buyer_cnt,
  sum(tpo.payment) as total_payment
from lucky_ethirdparty.t_third_parent_order tpo
where tpo.platform = 'TAOBAO'
  and tpo.status in ('WAIT_SELLER_SEND_GOODS', 'WAIT_BUYER_CONFIRM_GOODS',
                     'TRADE_BUYER_SIGNED', 'TRADE_FINISHED')
  and tpo.pay_time >= '2026-07-01'
  and tpo.pay_time < '2026-08-01';
```

关联：[[t_third_member]] · [[t_huibo_member_platform]] · [[数据字典索引]]
