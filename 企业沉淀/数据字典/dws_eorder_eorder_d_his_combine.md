---
created: 2026-07-24
tags: [企业, 数据, 字典, 电商]
field_status: 待补充
---

# dws_eorder_eorder_d_his_combine — 电商订单合并表

**数据库**：`dw_dws`

> ⚠️ **字段待补充**：请提供完整 DDL，我会补全所有 46 个字段。

## 已知字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `dt` | string | 分区字段，按日分区（如 `2026-07-23`），取 `date_sub(current_date(), 1)` |
| `id` | bigint |  |
| `mem_id` | bigint | 用户会员 ID |
| `member_no` | varchar | 会员编号 |
| `eorder_no` | varchar | 订单号 |
| `eorder_status` | varchar | 订单状态：`2`=待支付, `3`=已取消, `7`=待发货, `8`=已发货, `9`=已完成, `10`=已退款 |
| `eorder_pay_time` | datetime | 支付时间 |
| `total_ecmdty_payable_money` | decimal | 商品应付总金额（过滤 `<> 0` 排除无效订单） |
| `eorder_income` | decimal | 订单收入金额 |
| `merchant_type` | tinyint | 商家类型：`0`=自营, `1`=代销, `2`=POP |
| `sales_model` | tinyint | 销售模式：`1`=普通, `2`=众筹, `3`=预售 |
| `eorder_type` | tinyint | 订单类型：`1`=电商, `2`=卡券, `3`=供应商 |
| `payment_status` | tinyint | 支付状态：`10`=待付, `20`=部分付, `30`=已付 |
| ~~更多字段~~ | | 待补充 |
| `created_time` | datetime | 创建时间 |
| `modified_time` | datetime | 修改时间 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_member` | `mem_id` → `id` | 会员表 |

## 使用注意点

- **全量快照表**：每天一张完整快照，非增量，必须用 `dt` 分区过滤
- **有效订单**：`eorder_status IN ('2','3','7','8','9','10')`（排除 `1` 待审核、`4` 待确认、`5` 出库中、`6` 部分出库）
- **金额过滤**：`total_ecmdty_payable_money <> 0` 排除 0 元订单
- **支付时间**：按 `eorder_pay_time` 判断月/日，不要用 `created_time`
- **Spark SQL**：`now()` 可用，`DATEDIFF(month)` 不可用，用 `months_between`

关联：[[数据字典索引]]
