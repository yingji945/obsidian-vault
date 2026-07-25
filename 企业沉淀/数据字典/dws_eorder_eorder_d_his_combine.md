---
created: 2026-07-24
updated: 2026-07-24
tags: [企业, 数据, 字典, 电商]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-24
---

# dws_eorder_eorder_d_his_combine — 电商订单合并表

**数据库**：`dw_dws`

## 表结构（77 字段）

### 订单标识

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `eorder_id` | bigint | 主键 ID |
| 2 | `eorder_no` | varchar | 订单号 |
| 3 | `mem_id` | bigint | 会员 ID |
| 4 | `mem_name` | varchar | 会员名称 |
| 5 | `eorder_origin` | varchar | 订单来源 |

### 订单状态

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 6 | `eorder_status` | varchar | 订单状态：`1`=待付款, `2`=待发货, `3`=待收货, `4`=交易关闭, `5`=订单取消, `6`=订单取消售后中, `7`=部分退款成功, `8`=已签收, `9`=已签收售后中 |
| 7 | `refund_status` | varchar | 退款状态：`1`=不可退款, `2`=可退款, `3`=已新建, `4`=已退款, `5`=部分退款 |
| 8 | `invoice_status` | varchar | 发票状态：`1`=不可开票, `2`=可开票, `3`=已新建, `4`=已开票 |
| 9 | `payment_status` | varchar | 支付状态：`10`=待支付, `20`=已部分支付, `30`=已支付 |

### 时间戳

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 10 | `eorder_pay_time` | datetime | 支付时间 |
| 11 | `eorder_finish_time` | datetime | 完成时间 |
| 12 | `invoice_time` | datetime | 开票时间 |
| 13 | `eorder_cancel_time` | datetime | 取消时间 |
| 14 | `refund_time` | datetime | 退款时间 |
| 15 | `eorder_create_time` | datetime | 创建时间 |
| 16 | `update_time` | datetime | 修改时间 |
| 17 | `express_time` | datetime | 快递发出时间 |
| 18 | `deposit_pay_time` | datetime | 订金支付时间 |
| 19 | `stock_up_time` | datetime | 开始备货时间 |

### 订单属性

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 20 | `eorder_thirdparty_no` | varchar | 外部订单号 |
| 21 | `comment_status` | varchar | 评价状态：`0`=未评价, `1`=已评价 |
| 22 | `eorder_type` | varchar | 订单类型：`1`=电商, `2`=卡券, `3`=供应商 |
| 23 | `parent_eorder_no` | varchar | 父订单号（子订单的上级） |
| 24 | `sales_model` | varchar | 销售模式：`1`=普通销售, `2`=众筹销售, `3`=预售销售 |
| 25 | `crowd_funding_status` | varchar | 众筹状态：`1`=待完成, `2`=已完成 |
| 26 | `crowd_funding_result` | varchar | 众筹结果：`1`=成功, `2`=失败 |
| 27 | `is_stock_up` | varchar | 是否开始备货：`0`=否, `1`=是 |
| 28 | `is_delivery_overdue` | varchar | 是否发货逾期：`0`=否, `1`=是 |
| 29 | `delivery_status` | varchar | 发货状态：`1`=待发货, `2`=已发货, `3`=已部分发货 |
| 30 | `all_create_delivery` | varchar | 是否全部生成发货单：`0`=否, `1`=是 |
| 31 | `pay_task_no` | varchar | 收款任务编号 |
| 32 | `express_template_no` | varchar | 运费模板编号 |
| 33 | `express_template_name` | varchar | 运费模板名称 |
| 34 | `push_oms_flag` | varchar | 订单推送 OMS：`0`=未推送, `1`=e店宝, `2`=巨沃, `3`=旺店通 |

### 商家信息

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 35 | `merchant_id` | bigint | 店铺 ID |
| 36 | `eshop_name` | varchar | 店铺名称 |
| 37 | `merchant_name` | varchar | 商家名称 |
| 38 | `merchant_code` | varchar | 商家编码 |
| 39 | `merchant_type` | varchar | 店铺类型：`0`=自营商家, `1`=代销商家, `2`=POP 商家 |

### 金额字段

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 40 | `total_sale_money` | decimal | 总销售定价 |
| 41 | `eorder_income` | decimal | **订单收入** |
| 42 | `eorder_payable_money` | decimal | 订单应付金额 |
| 43 | `eorder_real_pay_money` | decimal | 订单实付金额 |
| 44 | `express_money` | decimal | 运费金额 |
| 45 | `total_ecmdty_payable_money` | decimal | **商品应付总金额**（过滤 `<> 0` 排除无效订单） |
| 46 | `total_ecmdty_addition_money` | decimal | 商品总附属金额 |
| 47 | `total_ecmdty_coupon_discount_money` | decimal | 商品总优惠券减免金额 |
| 48 | `may_refund_money` | decimal | 可退款金额 |
| 49 | `aldy_refund_money` | decimal | 已退款金额 |
| 50 | `real_pay_money_after_refund` | decimal | 退款后实付金额 |
| 51 | `may_invoice_money` | decimal | 可开票金额 |
| 52 | `aldy_invoice_money` | decimal | 已开票金额 |

### 优惠/活动分摊

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 53 | `wx_miniapp_discount_type` | varchar | 微信小程序减免类型：`1`=减免券 |
| 54 | `wx_miniapp_discount_money` | decimal | 微信小程序减免金额 |
| 55 | `total_activity_share_money` | decimal | 活动优惠的总金额 |
| 56 | `total_coupon_share_money` | decimal | 优惠券优惠金额 |
| 57 | `platform_activity_share_money` | decimal | 平台活动优惠的总金额 |
| 58 | `platform_coupon_share_money` | decimal | 平台优惠券优惠金额 |
| 59 | `pop_activity_share_money` | decimal | 商家活动优惠的总金额 |
| 60 | `pop_coupon_share_money` | decimal | 商家优惠券优惠金额 |
| 61 | `commission_money` | decimal | 佣金金额 |
| 62 | `wx_miniapp_discount_money_express` | decimal | 微信小程序减免金额（运费） |
| 63 | `wx_miniapp_discount_type_second` | varchar | 微信小程序减免类型 二次付款：`1`=减免券 |
| 64 | `wx_miniapp_discount_money_second` | decimal | 微信小程序减免金额 二次付款 |
| 65 | `express_discount_money` | decimal | 运费减免金额 |

### 取消原因

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 66 | `cancel_reason_id` | bigint | 取消原因主键（关联 `t_cancel_reason`） |
| 67 | `cancel_reason` | varchar | 取消原因文本 |
| 68 | `cancel_remark` | varchar | 取消备注 |
| 69 | `cancel_type` | varchar | 订单取消类型：`1`=用户, `2`=系统 |
| 70 | `cancel_user_type` | varchar | 取消人类型：`1`=用户, `2`=员工, `3`=系统, `4`=商家 |

### ETL 字段

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 71 | `dt` | string | **分区字段**，按日分区（如 `2026-07-23`） |
| 72 | `dw_create_time` | datetime | 数据加载时间 |
| 73 | `dw_program` | varchar | ETL 程序名称 |
| 74~77 | （其他预留字段） | | 待核实 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `t_member` | `mem_id` → `id` | 会员表 |

## 使用注意点

- **全量快照表**：每天一张完整快照，**必须用 `dt` 分区过滤**（`dt = date_sub(current_date(), 1)`）
- **有效订单**：`eorder_status IN (2,3,7,8,9)` — 待发货/待收货/部分退款成功/已签收/已签收售后中（排除 `1` 待付款、`4` 交易关闭、`5` 订单取消、`6` 取消售后中）
- **金额过滤**：`total_ecmdty_payable_money <> 0` 排除 0 元订单（无实际商品交易）
- **支付时间**：分析日月时按 `eorder_pay_time`，不要用 `eorder_create_time`
- **金额口径**：客单价分析用 `eorder_income`（订单收入）或 `total_ecmdty_payable_money`（商品应付），注意区分
- **店铺类型**：`merchant_type = 0` 自营走瑞幸自己的链路，`= 2` POP 是第三方商家
- **订单类型**：`eorder_type = 1` 电商实物订单，`= 2` 卡券类（电子兑换码），`= 3` 供应商订单
- **子父订单**：有拆单时子订单的 `parent_eorder_no` 指向父订单号，聚合时注意
- **Spark SQL**：`now()` 可用，`DATEDIFF(month)` 不可用，用 `months_between`

## 典型 SQL

```sql
-- 月度有效订单的客单价
select
  trunc(eorder_pay_time, 'MM') as month,
  count(distinct eorder_id) as order_cnt,
  count(distinct mem_id) as buyer_cnt,
  sum(eorder_income) as total_income,
  sum(eorder_income) / count(distinct mem_id) as avg_revenue_per_buyer
from dw_dws.dws_eorder_eorder_d_his_combine
where dt = date_sub(current_date(), 1)
  and eorder_status in ('2','3','7','8','9')
  and total_ecmdty_payable_money <> 0
  and eorder_pay_time >= '2026-06-01'
  and eorder_pay_time < '2026-07-01'
group by trunc(eorder_pay_time, 'MM');
```

关联：[[数据字典索引]]
