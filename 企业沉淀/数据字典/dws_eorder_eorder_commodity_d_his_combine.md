---
created: 2026-08-05
updated: 2026-08-07
tags: [企业, 数据, 字典, 电商]
field_status: ✅ 完整
source: 用户提供 @ 2026-08-05
---

# dws_eorder_eorder_commodity_d_his_combine — 电商订单商品合并表

**数据库**：`dw_dws`

## 表说明

- **粒度**：订单商品行（**一个订单可能多行商品**，主键 `eorder_ecmdty_id`）
- 与 `dws_eorder_eorder_d_his_combine`（订单级）的关系：**1 订单 : N 商品行**，通过 `eorder_id` 关联
- 用途：**商品维度分析**——SKU 销售、商品/品牌/类目渗透、赠品、营销分摊到商品行、售后
- **全量快照表，按日分区（dt）**（用户确认 2026-08-07）；字段清单未展示 `dt`，但按 `d_his_combine` 同族命名与快照语义推断为按日分区

## 表结构（82 字段）

### 订单标识（冗余自订单表，一单多行重复）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `eorder_ecmdty_id` | bigint | **主键：订单商品 ID** |
| 2 | `eorder_id` | bigint | 订单主键 ID |
| 3 | `eorder_no` | varchar | 订单号 |
| 4 | `eorder_origin` | varchar | 订单来源 |
| 5 | `eorder_status` | varchar | 订单状态：`1`=待付款, `2`=待发货, `3`=待收货, `4`=交易关闭, `5`=订单取消, `6`=订单取消售后中, `7`=部分退款成功, `8`=已签收, `9`=已签收售后中, `10`=待收货售后中(2026-08扩充) |
| 6 | `eorder_pay_time` | datetime | 订单支付时间 |
| 7 | `eorder_finish_time` | datetime | 订单完成时间 |
| 8 | `eorder_create_time` | datetime | 订单创建时间 |
| 9 | `eorder_type` | varchar | 订单类型：`1`=电商, `2`=卡券, `3`=供应商 |
| 10 | `mem_id` | bigint | 会员 ID |

### 商品维度（本表核心新增）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 11 | `ecmdty_id` | bigint | 商品 ID |
| 12 | `ecmdty_code` | varchar | 商品编号 |
| 13 | `ecmdty_name` | varchar | 商品名称 |
| 14 | `ecmdty_type` | varchar | 商品类型：`1`=实物, `2`=虚拟 |
| 15 | `pop_brand_code` | varchar | 品牌编号 |
| 16 | `pop_brand_name` | varchar | 品牌名称 |
| 17 | `pop_brand_en_name` | varchar | 品牌英文名称 |
| 18 | `one_category_code` | varchar | 商品一级分类 code |
| 19 | `one_category_name` | varchar | 商品一级分类名称 |
| 20 | `one_category_en_name` | varchar | 一级分类英文名称 |
| 21 | `two_category_code` | varchar | 商品二级分类 code |
| 22 | `two_category_name` | varchar | 商品二级分类名称 |
| 23 | `two_category_en_name` | varchar | 二级分类英文名称 |
| 24 | `three_category_code` | varchar | 商品三级分类 code |
| 25 | `three_category_name` | varchar | 商品三级分类名称 |
| 26 | `three_category_en_name` | varchar | 三级分类英文名称 |
| 27 | `ecmdty_barcode` | varchar | 商品条形码 |
| 28 | `ecmdty_addition` | varchar | 附属商品属性 |
| 29 | `esku_code` | varchar | 商品 SKU 编码 |
| 30 | `esku_id` | bigint | 电商 SKU ID |
| 31 | `esupplier_id` | bigint | 供应商 ID |
| 32 | `is_gift` | varchar | 是否赠品：`0`=否, `1`=是 |

### 商品金额（行级）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 33 | `ecmdty_origin_money` | decimal | 商品原价 |
| 34 | `ecmdty_sale_money` | decimal | 销售定价 |
| 35 | `ecmdty_addition_money` | decimal | 附属费用 |
| 36 | `ecmdty_payable_money` | decimal | 商品应付 |
| 37 | `ecmdty_real_pay_money` | decimal | 商品实付 |
| 38 | `ecmdty_real_income` | decimal | **商品收入**（行级收入；⚠️ 与订单级收入**可能不一致**，暂不处理） |

### 优惠券

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 39 | `coupon_proposal_id` | bigint | 优惠券方案 ID |
| 40 | `coupon_no` | varchar | 优惠券发送记录编号 |
| 41 | `coupon_template_id` | bigint | 优惠券模板 ID |
| 42 | `coupon_template_no` | varchar | 优惠券编号 |
| 43 | `coupon_template_name` | varchar | 优惠券模板名称 |
| 44 | `coupon_discount_money` | decimal | 优惠券减免金额 |
| 45 | `wx_miniapp_discount_type` | varchar | 微信小程序减免类型：`1`=减免券 |
| 46 | `wx_miniapp_discount_money` | decimal | 微信小程序减免金额 |
| 47 | `wx_miniapp_discount_type_second` | varchar | 微信小程序减免类型（二次付款）：`1`=减免券 |
| 48 | `wx_miniapp_discount_money_second` | decimal | 微信小程序减免金额（二次付款） |

### 活动/营销

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 49 | `activity_id` | bigint | 命中的活动 ID |
| 50 | `activity_type` | varchar | 活动类型 |
| 51 | `marketing_solution_no` | varchar | 营销方案编号 |

### 优惠分摊（行级，营销/优惠券按商品行分摊）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 52 | `activity_share_money` | decimal | 营销活动优惠分摊金额 |
| 53 | `coupon_share_money` | decimal | 优惠券优惠分摊金额 |
| 54 | `platform_activity_share_money` | decimal | 平台营销活动优惠分摊金额 |
| 55 | `platform_coupon_share_money` | decimal | 平台优惠券优惠分摊金额 |
| 56 | `pop_activity_share_money` | decimal | 商家营销活动优惠分摊金额 |
| 57 | `pop_coupon_share_money` | decimal | 商家优惠券优惠分摊金额 |
| 58 | `express_real_pay_money` | decimal | 快递分摊实付金额 |
| 59 | `wx_miniapp_discount_money_express` | decimal | 微信小程序减免金额（运费分摊） |
| 60 | `ecmdty_commission_money` | decimal | 佣金金额 |
| 61 | `ecmdty_refund_commission_money` | decimal | 可退佣金金额 |

### 发票

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 62 | `invoice_status` | varchar | 发票状态：`1`=不可开票, `2`=可开票, `3`=已新建, `4`=已开票 |
| 63 | `may_invoice_money` | decimal | 可开票金额 |
| 64 | `aldy_invoice_money` | decimal | 已开票金额 |

### 退款/售后

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 65 | `refund_status` | varchar | 退款状态：`1`=不可退款, `2`=可退款, `3`=已新建, `4`=已退款, `5`=部分退款 |
| 66 | `may_refund_money` | decimal | 可退款金额 |
| 67 | `aldy_refund_money` | decimal | 已退款金额 |
| 68 | `merchant_bear_money` | decimal | 商品退款商家承担金额 |
| 69 | `remit_money` | decimal | 打款金额 |
| 70 | `merchant_bear_remit_money` | decimal | 商家承担打款金额 |
| 71 | `aftersale_status` | varchar | 售后状态：`1`=未发起售后, `2`=已发起售后, `3`=已完成处理 |
| 72 | `aftersale_type` | varchar | 售后类型：`1`=取消订单, `2`=退货退款, `3`=退款不退货, `4`=换货 |

### 商家/店铺

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 73 | `merchant_code` | varchar | 商家编码 |
| 74 | `merchant_id` | bigint | 商家主键 ID |
| 75 | `merchant_name` | varchar | 商家名称 |
| 76 | `eshop_name` | varchar | 店铺名称 |
| 77 | `merchant_type` | varchar | 商家类型：`0`=自营商家, `1`=代销商家, `2`=POP 商家 |

### 发货/其他

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 78 | `delivery_status` | varchar | 发货状态：`1`=待发货, `2`=已新建, `3`=已发货, `4`=已签收 |
| 79 | `create_time` | datetime | 创建时间 |
| 80 | `update_time` | datetime | 修改时间 |

### ETL

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 81 | `dw_create_time` | datetime | 数据加载时间 |
| 82 | `dw_program` | varchar | ETL 程序名称 |

## 关联键

| 关联表 | 关联字段 | 说明 |
|:------|:--------|:-----|
| `dws_eorder_eorder_d_his_combine` | `eorder_id` → `eorder_id` | 订单级表（1:N，本表为明细） |
| `t_member` | `mem_id` → `id` | 会员表 |

## 使用注意点

- **商品行粒度**：一个订单多行商品时，`eorder_id` 重复；按订单统计需先 `GROUP BY eorder_id` 或 `DISTINCT`
- **金额口径**：行级金额用 `ecmdty_real_income`（商品收入）；⚠️ 订单级收入与行收入之和**可能不一致**（用户确认 2026-08-07，暂不处理；用数前先核对口径）
- **有效订单**：`eorder_status IN ('2','3','7','8','9','10')`（与订单表一致，含 2026-08 扩充的 10 待收货售后中）
- **自营口径**：`merchant_type = 0`（自营商家）
- **赠品**：`is_gift = 1` 是赠品行，商品分析（销量/收入）注意是否排除
- **分类**：三级分类（one/two/three_category_*），英文名/中文名齐备
- **营销分摊**：`*_share_money` 字段为营销/优惠券按商品行分摊金额，可用于活动 ROI 的商品级归因
- **⚠️ delivery_status 枚举与订单表不同（已确认 2026-08-07）**：本表 `1`=待发货, `2`=已新建, `3`=已发货, `4`=已签收；订单表 `dws_eorder_eorder_d_his_combine` 是 `1`=待发货, `2`=已发货, `3`=已部分发货——**同名不同义，勿混用**
- **dt 分区**：字段清单未含 `dt`；**全量快照表**（用户确认 2026-08-07），按日分区，取最新分区即当日全量

## 典型 SQL

```sql
-- 商品维度：近30天自营渠道商品销售额 Top 20（按商品行收入）
SELECT
  ecmdty_id,
  ecmdty_name,
  one_category_name,
  two_category_name,
  COUNT(DISTINCT eorder_id) AS order_cnt,
  COUNT(*) AS line_cnt,
  SUM(ecmdty_real_income) AS income
FROM dw_dws.dws_eorder_eorder_commodity_d_his_combine
WHERE dt = DATE_SUB(CURRENT_DATE(), 1)          -- 快照分区（全量快照表，取最新分区）
  AND merchant_type = 0
  AND eorder_status IN ('2','3','7','8','9','10')
  AND is_gift = 0
  AND eorder_pay_time >= DATE_SUB(CURRENT_DATE(), 30)
GROUP BY ecmdty_id, ecmdty_name, one_category_name, two_category_name
ORDER BY income DESC
LIMIT 20;
```

关联：[[数据字典索引]] · [[dws_eorder_eorder_d_his_combine]]
