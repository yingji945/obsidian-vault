---
created: 2026-11-05
updated: 2026-11-05
tags: [企业, 数据, 字典, 电商]
field_status: ✅ 完整
source: 用户提供 @ 2026-11-05（完整 DDL 字段清单）
---

# fact_dwd_eord_eorder_commodity_d_his — 电商订单商品信息表

**数据库**：`dw_dwd`（DWD 层）　**字段数**：84 + 分区字段 `dt`

## 表说明

- **粒度**：订单商品行（**一个订单可能多行商品**），主键 `eorder_ecmdty_id`
- **与订单主表的关系**：`1 订单 : N 商品行`，通过 `eorder_id` 关联 `[[dws_eorder_eorder_d_his_combine]]`
- **用途**：SKU 级销售分析、商品/类目渗透、赠品与营销分摊到行、售后
- **全量快照**：`_his` 后缀，`dt` 分区内含**全部历史**（实测 2026-03-26 起数据都在一个分区里）→ **时间必须靠订单表的 `eorder_pay_time` 卡，不能靠 `dt`**

## 🔴 三个必须先知道的坑

| # | 坑 | 说明 |
|:-:|:--|:--|
| 1 | **没有支付时间** | 只有 `create_time` / `update_time`（记录创建与修改），**没有 `eorder_pay_time`** → 所有按支付时间的分析必须 join 订单主表 |
| 2 | **没有订单状态、没有 `merchant_type`** | 无法自行排除待付款/取消单，也无法限定自营 → 同样 join 订单主表 |
| 3 | **有 `delete_flag`** | `0`=否 `1`=是，**查询时必须加 `coalesce(delete_flag,'0') = '0'`**，否则会把已删除行算进去 |

**标准 join 写法**：

```sql
from dw_dwd.fact_dwd_eord_eorder_commodity_d_his c
join dw_dws.dws_eorder_eorder_d_his_combine o
  on c.eorder_id = o.eorder_id
 and o.dt = date_sub(current_date(), 1)
where c.dt = date_sub(current_date(), 1)
  and coalesce(c.delete_flag, '0') = '0'
  and o.merchant_type = 0
  and o.eorder_status in ('2','3','7','8','9','10')
```

## 表结构（84 字段）

### 订单标识（冗余自订单表）

| # | 字段名 | 说明 |
|:-:|:--|:--|
| 1 | `eorder_ecmdty_id` | **主键：订单商品 ID** |
| 2 | `eorder_id` | 订单主键 ID（关联订单主表） |
| 3 | `mem_id` | 会员 ID |

### 商品维度

| # | 字段名 | 说明 |
|:-:|:--|:--|
| 4 | `ecmdty_id` | 商品 ID |
| 5 | `ecmdty_sale_id` | 商品销售 ID |
| 6 | `ecmdty_sale_plan_id` | 商品销售方案 ID |
| 7 | `ecmdty_code` | 商品编号 |
| 8 | `ecmdty_name` | 商品名称 |
| 9 | `ecmdty_size_id` | 商品大小 ID |
| 10 | `ecmdty_size` | 商品大小 |
| 11 | `ecmdty_sale_unit` | 商品销售单位 |
| 12 | `ecmdty_temper` | 商品冷热属性 |
| 13 | `ecmdty_barcode` | 商品条形码 |
| 14 | `ecmdty_addition` | 附属商品属性 |
| 45 | `ecmdty_specification` | 货物规格 |
| 46 | `gross_weight` | 毛重 |
| 47 | `net_weight` | 净重 |
| 64 | `ecmdty_image_url` | 商品图片地址 |
| 76 | `ecmdty_market_price` | 商品市场价 |
| **51** | **`esku_code`** | **商品 SKU 编码** ← SKU 级分析用这个 |
| 52 | `esupplier_id` | 供应商 ID |
| 68 | `merchant_code` | 商家编码 |

### 金额

| # | 字段名 | 说明 |
|:-:|:--|:--|
| 15 | `ecmdty_sale_money` | **销售定价（单件标价）** ← 做价格分档用这个 |
| 16 | `ecmdty_addition_money` | 附属费用 |
| 19 | `ecmdty_payable_money` | 商品应付（**行级总价**，可能含多件） |
| 20 | `ecmdty_real_pay_money` | 商品实付（行级） |
| 21 | `ecmdty_real_income` | 商品收入 |
| 48 | `ecmdty_origin_money` | 商品原价 |
| 59 | `express_real_pay_money` | 快递分摊实付金额 |
| 60 | `commission_rate` | 佣金费率（四位小数） |
| 61 | `ecmdty_commission_money` | 佣金金额 |
| 62 | `ecmdty_refund_commission_money` | 可退佣金金额 |
| 70 | `merchant_bear_money` | 商品退款商家承担金额 |
| 71 | `remit_money` | 打款金额 |
| 72 | `merchant_bear_remit_money` | 商家承担打款金额 |

> ⚠️ **`ecmdty_sale_money`（标价）vs `ecmdty_payable_money`（行级总价）**：做价格分档/正装判定用前者，做金额汇总用后者或 `ecmdty_real_pay_money`。

### 优惠与分摊

| # | 字段名 | 说明 |
|:-:|:--|:--|
| 28 | `coupon_proposal_id` | 优惠券方案 id |
| 29 | `coupon_no` | 优惠券发送记录编号 |
| 30 | `coupon_template_name` | 优惠券名称 |
| 31 | `coupon_type` | 代金券一级类型 |
| 32 | `coupon_sub_type` | 优惠券二级类型 |
| 33 | `coupon_commission_money` | 基础提成金额 |
| 34 | `coupon_commission_rate` | 优惠券基础提成比例 |
| 35 | `coupon_discount_money` | 优惠券减免金额 |
| 36 | `return_coupon_commission_money` | 已退基础提成金额 |
| 65 | `coupon_template_id` | 优惠券模板 id |
| 78 | `coupon_template_no` | 优惠券编号 |
| 37 | `wx_miniapp_discount_type` | 微信小程序减免类型（1=减免券） |
| 38 | `wx_miniapp_discount_money` | 微信小程序减免金额 |
| 66 | `wx_miniapp_discount_money_express` | 微信小程序减免金额（运费分摊） |
| 79 | `wx_miniapp_discount_type_second` | 微信小程序减免类型（二次付款，1=减免券） |
| 80 | `wx_miniapp_discount_money_second` | 微信小程序减免金额（二次付款） |
| 53 | `activity_share_money` | 营销活动优惠分摊金额 |
| 54 | `coupon_share_money` | 优惠券优惠分摊金额 |
| 55 | `platform_activity_share_money` | 平台营销活动优惠分摊 |
| 56 | `platform_coupon_share_money` | 平台优惠券优惠分摊 |
| 57 | `pop_activity_share_money` | 商家营销活动优惠分摊 |
| 58 | `pop_coupon_share_money` | 商家优惠券优惠分摊 |
| 42 | `activity_id` | 命中的活动 id |
| 43 | `activity_group` | 命中活动的组序号 |
| 67 | `activity_type` | 活动类型 |
| 44 | `source_order_no` | 裂变源单号 |
| 77 | `marketing_solution_no` | 营销方案编号 |
| 81 | `marketing_solution_name` | 营销方案名称 |
| 82 | `marketing_rule_hit` | 营销规则命中 |

### 状态类

| # | 字段名 | 说明 |
|:-:|:--|:--|
| 17 | `ecmdty_situation` | 商品情况：`0`正常 `1`仅退款 `2`退货退款 `3`退货退款且打款 `4`仅打款 |
| 18 | `ecmdty_return_exchange_reason` | 商品退换货原因 |
| 22 | `invoice_status` | 发票状态：`1`不可开票 `2`可开票 `3`已新建 `4`已开票 |
| 23 | `may_invoice_money` | 可开票金额 |
| 24 | `aldy_invoice_money` | 已开票金额 |
| 25 | `refund_status` | 退款状态：`1`不可退款 `2`可退款 `3`已新建 `4`已退款 `5`部分退款 |
| 26 | `may_refund_money` | 可退款金额 |
| 27 | `aldy_refund_money` | 已退款金额 |
| 49 | `is_gift` | 是否赠品：`0`否 `1`是 |
| 50 | `two_sale` | 当前 SKU 是否已发生过售后：`0`否 `1`是 |
| **39** | **`delete_flag`** | **是否已删除：`0`否 `1`是** ← 必须过滤 |
| 69 | `ecmdty_purchase_handle` | 商品采购处理：`1`负数清算 `2`正常清算 |
| 73 | `delivery_status` | 发货状态：`1`待发货 `2`已新建 `3`已发货 `4`已签收 |
| 74 | `aftersale_status` | 售后状态：`1`未发起售后 `2`已发起售后 `3`已完成处理 |
| 75 | `aftersale_type` | 售后类型：`1`取消订单 `2`退货退款 `3`退款不退货 `4`换货 |
| 63 | `express_id` | 发货物流 id |

### 时间与 ETL

| # | 字段名 | 说明 |
|:-:|:--|:--|
| 40 | `create_time` | 创建时间（**不是支付时间**） |
| 41 | `update_time` | 修改时间 |
| 83 | `dw_create_time` | 数据加载时间 |
| 84 | `dw_program` | ETL 程序名称 |
| — | `dt` | **分区字段**（全量快照，一个分区含全部历史） |

## 常用取数片段

**按 SKU 看月度销售**：
```sql
select
  left(date(o.eorder_pay_time), 7) as ym
  , count(distinct c.mem_id)                  as 买家数
  , count(*)                                  as 件数
  , round(sum(coalesce(c.ecmdty_real_pay_money, 0)), 2) as 实付
from dw_dwd.fact_dwd_eord_eorder_commodity_d_his c
join dw_dws.dws_eorder_eorder_d_his_combine o
  on c.eorder_id = o.eorder_id and o.dt = date_sub(current_date(), 1)
where c.dt = date_sub(current_date(), 1)
  and c.esku_code = '你的SKU'
  and coalesce(c.delete_flag, '0') = '0'
  and o.merchant_type = 0
  and o.eorder_status in ('2','3','7','8','9','10')
group by 1
```

> 关联：[[dws_eorder_eorder_d_his_combine]] · [[数据字典索引]] · [[引流品转化评估SQL模板]] · [[试用装转化分析-P04672-000003]]
