---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 门店业务域, 门店订单, DWM, 渠道归因]
field_status: ✅ 完整（164/164 字段类型已确定）
source: 用户提供（2026-10-12）：SELECT 字段列表 + 物化视图加工 SQL
---

# dw_dwm.dwm_mg_order_cmdty_market_wide_d_view

> **订单商品渠道归因视图** —— 门店业务（瑞幸咖啡门店：线下取餐 + 门店配送）
> 粒度：1 行 = 1 个订单商品（`order_cmdty_id`）· 分区：`dt`（订单创建日期）· 字段数：**164**

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_dwm.dwm_mg_order_cmdty_market_wide_d_view` |
| 业务域 | **门店业务域**（门店业务，2026-10-12 新建） |
| 业务范围 | 瑞幸门店零售订单：**线下取餐 + 门店配送**（外卖 / 自取 / 自助） |
| 粒度 | 订单商品行（1 订单商品 = 1 行） |
| 层级 | `DWM`（明细中间层宽表 / 视图） |
| 分区键 | `dt` = 订单创建日期 |
| 字段数 | 164（11 组，见第三节） |

> ⚠️ **与电商域严格区分**：本表是**门店订单**（门店现制饮品，APP/小程序点单），
> 与 [[dws_eorder_eorder_commodity_d_his_combine]]（**即享商城**电商订单商品）**不是一条业务线**，
> 口径、字段、状态枚举均不通用。速记：电商表 `eorder_*`，本表 `order_*`。

---

## 二、血缘与物化逻辑 ⭐

本视图由 **4 张表**加工而成（依据用户提供的定义 SQL）：

| 来源表 | 别名 | 贡献 |
|:--|:--|:--|
| `dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc` | `oc` | **主表**（增量）：订单 / 门店 / 商品 / 营销 / 金额全部基础字段 |
| [[dwm_mg_order_cmdty_channel_bridge_d_inc]] | `cb` | 渠道桥表：`fourth_channel_id`、`third_site_channel_*`（**无渠道名**，名称在渠道层级维） |
| `dw_dim.dim_channel_level_d_his` | `cl` | 渠道层级维：`first / second / third_channel_*`、`fourth_channel_name` |
| [[dim_sku_ord_rmk_d_a]] | `sku` | **订单商品属性维**：`cup_rmk_name`、`temp_rmk_name` |

**JOIN 条件**

```sql
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc oc
left join dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc cb
       on oc.dt = cb.dt and oc.order_cmdty_id = cb.order_cmdty_id
left join dw_dim.dim_channel_level_d_his cl
       on cb.fourth_channel_id = cl.fourth_channel_id
      and cl.dt = date_sub(current_date(), 1)
left join dw_dim.dim_sku_ord_rmk_d_a sku
       on oc.sku_code = sku.sku_code
      and sku.dt = date_sub(current_date(), 1)
```

> ⚠️ **维表分区口径不一致**：`cl` / `sku` 用 `dt = date_sub(current_date(),1)` 取**最新快照**，**不跟随** `oc.dt`；
> 只有渠道桥 `cb` 是按 `dt + order_cmdty_id` 与主表对齐的。

### 2.1 三个「新口径」字段怎么算（重点）

字段名带 `new_` 的 3 个字段是**视图内重算**的，不是上游直取：

**① `new_voucher_share_amt`（优惠分摊金额-新）**

```sql
if(oc.one_category_name <> '周边商品',
   oc.voucher_share_amt * (
       oc.cmdty_origin_amt
       / sum(case when oc.order_status = 50
                   and oc.order_cmdty_situation != 2
                   and oc.one_category_name <> '周边商品'
                  then oc.cmdty_origin_amt else 0 end)
         over (partition by oc.dt, oc.voucher_no)
   ),
   0) as new_voucher_share_amt
```

**② `new_company_real_income_share_amt`（优惠分摊金额(公司实收)-新）** —— 算法同上，仅把分子换成 `oc.company_real_income_share_amt`。

**③ `new_user_pay_money`（用户实付-新）**

```sql
case when cl.third_channel_name = '抖音'
     then coalesce(oc.cmdty_pay_amt, 0)
          + if(oc.one_category_name <> '周边商品',
               oc.voucher_share_amt * (<同①的窗口分摊系数>) * coalesce(oc.month_exchange_rate, 1),
               0)
     else oc.user_pay_money
end as new_user_pay_money
```

**共同点（口径三要素）**：

1. **按券分摊**：窗口是 `partition by dt, voucher_no`（同一张券在同一天的所有订单商品之间按**商品定价**加权摊销）
2. **周边商品不参与**：`one_category_name <> '周边商品'`，周边商品的分摊额直接给 **0**
3. **有效性条件**：分母只累计 `order_status = 50` **且** `order_cmdty_situation != 2`（排除损耗）的商品

---

## 三、字段清单（164 字段 · 11 组）

> **类型来源（164/164 全覆盖）**：161 个继承自上游（主表 149 + 渠道桥 3 + 渠道层级维 7 + 商品属性维 2）；标 `*` 的 3 个为视图内计算字段（按参与运算字段推断）。

#### A. 主键与订单标识（12 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `dt` | `string` | 订单创建日期 |
| 2 | `order_cmdty_id` | `bigint` | 订单商品ID |
| 3 | `order_id` | `bigint` | 订单ID |
| 4 | `order_no` | `string` | 订单编号 |
| 5 | `mem_id` | `bigint` | 会员id |
| 6 | `dept_id` | `bigint` | 部门id |
| 7 | `order_status` | `int` | 订单状态 |
| 8 | `order_origin` | `int` | 订单来源 |
| 9 | `order_channel` | `int` | 订单渠道 |
| 10 | `order_type` | `int` | 订单类型:外卖订单/自取订单/ 自助订单 |
| 11 | `actual_order_type` | `int` | 实际订单类型 |
| 12 | `order_cmdty_situation` | `int` | 商品情况 参见枚举 1正常 2损耗 3换货 |

#### B. 履约与配送（11 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 13 | `exp_getit_type` | `int` | 取餐方式 |
| 14 | `exp_disp_type` | `int` | 接单类型(预留字段)（1-配送人接单、2-门店指派） |
| 15 | `retain_interval_time` | `int` | 保鲜时段 |
| 16 | `time_slice_half_hour` | `string` | 半小时时段 |
| 17 | `supplier_id` | `int` | 配送商id |
| 18 | `supplier_no` | `string` | 配送商编号 |
| 19 | `supplier_name` | `string` | 配送商名称 |
| 20 | `supplier_type` | `int` | 配送商类型 |
| 21 | `exp_distance` | `decimal(19, 4)` | 配送距离 |
| 22 | `delivery_income_amt` | `decimal(19, 4)` | 配送费收入(非周边商品分摊) |
| 23 | `delivery_pay_share_amt` | `decimal(19, 4)` | 配送费实付(非周边商品分摊) |

#### C. 时间戳（11 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 24 | `order_create_time` | `timestamp` | 订单创建时间 |
| 25 | `order_update_time` | `timestamp` | 订单修改时间 |
| 26 | `order_pay_time` | `timestamp` | 订单支付时间 |
| 27 | `order_finish_time` | `timestamp` | 订单完成时间 |
| 28 | `product_accept_time` | `timestamp` | 接单时间（开始制作时间） |
| 29 | `product_finish_time` | `timestamp` | 制作完成时间 |
| 30 | `exp_getit_time` | `timestamp` | 取餐时间 |
| 31 | `exp_finish_time` | `timestamp` | 配送完成时间 |
| 32 | `refund_time` | `timestamp` | 退款时间 |
| 33 | `set_up_time` | `timestamp` | 开业时间 |
| 34 | `commodity_actual_launch_date` | `string` | 上市时间 |

#### D. 状态与标记（10 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 35 | `pay_from` | `int` | 支付方式（微信、支付宝、银联，来源：配置中心） |
| 36 | `group_order` | `int` | 拼单类型（0-普通，1-拼单） |
| 37 | `income_status` | `int` | 商品收入状态 |
| 38 | `invoice_status` | `int` | 商品开票状态 |
| 39 | `refund_status` | `int` | 商品退款状态 |
| 40 | `refund_origin` | `int` | 退款来源 1自动2人工 |
| 41 | `is_custome` | `int` | 是否客制化0否1是 |
| 42 | `is_gift` | `int` | 是否是赠送商品0否1是 |
| 43 | `is_99_coupon` | `int` | 是否使用99券 |
| 44 | `is_multi_cup` | `int` | 是否一单多杯 |

#### E. 渠道归因（含三方）（12 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 45 | `third_order_id` | `bigint` | 三方渠道订单ID |
| 46 | `third_order_no` | `string` | 三方渠道订单编号 |
| 47 | `first_channel_id` | `int` | 一级渠道id |
| 48 | `first_channel_name` | `string` | 一级渠道名称 |
| 49 | `second_channel_id` | `int` | 二级渠道id |
| 50 | `second_channel_name` | `string` | 二级渠道名称 |
| 51 | `third_channel_id` | `bigint` | 三级渠道id |
| 52 | `third_channel_name` | `string` | 三级渠道名称 |
| 53 | `fourth_channel_id` | `bigint` | 四级渠道id |
| 54 | `fourth_channel_name` | `string` | 四级渠道名称 |
| 55 | `third_site_channel_id` | `bigint` | 三方渠道场域ID |
| 56 | `third_site_channel_name` | `string` | 三方渠道场域名称 |

#### F. 门店与区域（17 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 57 | `shop_id` | `bigint` | 门店id |
| 58 | `shop_no` | `string` | 门店编号 |
| 59 | `shop_name` | `string` | 门店名称 |
| 60 | `shop_type` | `int` | 门店类型 |
| 61 | `shop_level` | `int` | 门店层级:快取店/悠享店/外卖厨房/快闪店/瑞即购/企业内部店/旗舰店 |
| 62 | `shop_price_level` | `bigint` | 商品价位级别 |
| 63 | `coop_pattern_code` | `string` | 运营合作模式主数据编号：直营，代理 |
| 64 | `coop_pattern_name` | `string` | 运营合作模式名称：直营，代理 |
| 65 | `area_id` | `bigint` | 区域ID |
| 66 | `area_name` | `string` | 区域 |
| 67 | `city_id` | `bigint` | 城市ID |
| 68 | `city_name` | `string` | 城市 |
| 69 | `city_tier` | `int` | 城市等级 0 新一线 1 一线 2 二线 3 三线 4 四线 |
| 70 | `prov_id` | `bigint` | 省份id |
| 71 | `prov_name` | `string` | 省份 |
| 72 | `business_region_code` | `string` | 经营区域code |
| 73 | `business_region_name` | `string` | 经营区域名称 |

#### G. 商品与 SKU（20 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 74 | `cmdty_id` | `bigint` | 商品ID |
| 75 | `cmdty_sale_id` | `bigint` | 商品销售ID |
| 76 | `cmdty_sale_plan_id` | `bigint` | 商品销售方案ID |
| 77 | `cmdty_sale_unit` | `int` | 商品销售单位 |
| 78 | `cmdty_code` | `string` | 商品编号 |
| 79 | `cmdty_name` | `string` | 商品名称 |
| 80 | `cmdty_size` | `string` | 商品大小 |
| 81 | `cmdty_temper` | `string` | 商品冷热属性 |
| 82 | `cmdty_mode` | `int` | 商品类型 参见枚举 现制商品 外购商品 |
| 83 | `one_category_name` | `string` | 商品一级分类名称 |
| 84 | `two_category_name` | `string` | 商品二级分类名称 |
| 85 | `three_category_name` | `string` | 商品三级分类名称 |
| 86 | `cmdty_theme` | `string` | 商品主题 |
| 87 | `cmdty_series` | `string` | 商品系列 |
| 88 | `cmdty_texture` | `string` | 商品浓度 |
| 89 | `sku_code` | `string` | sku编码 |
| 90 | `sku_name` | `string` | sku名称 |
| 91 | `cup_rmk_name` | `string` | 杯型(新) |
| 92 | `temp_rmk_name` | `string` | 温度(新) |
| 93 | `business_cmdty_name` | `string` | 业务商品名称，若无业务商品，则为商品名称 |

#### H. 套餐（6 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 94 | `package_id` | `bigint` | 商品系统套餐ID |
| 95 | `package_code` | `string` | 商品系统套餐CODE |
| 96 | `package_name` | `string` | 商品系统套餐NAME |
| 97 | `package_batch_no` | `int` | 批次号 套餐多份时展示使用 |
| 98 | `package_type` | `int` | 套餐类型(1为自营套餐，2为渠道套餐) |
| 99 | `package_sub_type` | `int` | 套餐子类型 1 预存套餐 |

#### I. 优惠与营销活动（31 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 100 | `market_id` | `bigint` | 营销活动ID |
| 101 | `market_name` | `string` | 营销活动名称 |
| 102 | `market_type` | `int` | 营销活动类型 |
| 103 | `market_sub_type` | `int` | 营销活动子类型 |
| 104 | `company_discount_type` | `int` | 企业优惠类型 |
| 105 | `company_discount_id` | `bigint` | 企业优惠id |
| 106 | `company_discount_name` | `string` | 企业优惠名称 |
| 107 | `voucher_id` | `bigint` | 优惠id |
| 108 | `voucher_no` | `string` | 优惠编号 |
| 109 | `voucher_type` | `int` | 优惠类型 1优惠券 2咖啡库券 3阶梯次卡 |
| 110 | `voucher_origin` | `int` | 优惠来源 |
| 111 | `voucher_status` | `int` | 优惠状态 |
| 112 | `template_id` | `bigint` | 优惠模板id |
| 113 | `template_name` | `string` | 优惠模板名称 |
| 114 | `template_type` | `int` | 优惠模板类别 |
| 115 | `proposal_id` | `bigint` | 优惠方案ID |
| 116 | `proposal_no` | `string` | 优惠方案编号 |
| 117 | `proposal_name` | `string` | 优惠方案名称 |
| 118 | `proposal_type_name` | `string` | 优惠方案类型名称 |
| 119 | `proposal_sub_type_name` | `string` | 优惠方案子类型名称 |
| 120 | `discount_type` | `int` | 打折类型 |
| 121 | `discount_sub_type` | `int` | 打折子类型 |
| 122 | `allowance_project_id` | `bigint` | 一级补贴项目ID |
| 123 | `allowance_project_no` | `string` | 一级补贴项目编号 |
| 124 | `allowance_project_name` | `string` | 一级补贴项目名称 |
| 125 | `sub_allowance_project_id` | `bigint` | 二级补贴项目ID |
| 126 | `sub_allowance_project_no` | `string` | 二级补贴项目编号 |
| 127 | `sub_allowance_project_name` | `string` | 二级补贴项目名称 |
| 128 | `voucher_share_amt` | `decimal(19, 4)` | 优惠分摊金额 |
| 129 | `market_amt` | `decimal(19, 4)` | 营销活动优惠价格 |
| 130 | `company_discount_amt` | `decimal(19, 4)` | 企业减免金额 |

#### J. 三方金额与补贴（12 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 131 | `third_discnt_amt` | `decimal(19, 4)` | 三方商品折扣后金额 |
| 132 | `third_mkt_amt` | `decimal(19, 4)` | 三方其他商品减免金额 |
| 133 | `third_pay_amt` | `decimal(19, 4)` | 三方用户实付 |
| 134 | `third_red_packet_amt` | `decimal(19, 4)` | 三方红包分摊金额 |
| 135 | `third_packing_charge_amt` | `decimal(19, 4)` | 三方打包费 |
| 136 | `third_allowance_share_amt` | `decimal(19, 4)` | 三方补贴分摊至商品 |
| 137 | `total_subsidy_amt` | `decimal(19, 4)` | 总补贴金额 |
| 138 | `luckin_subsidy_amt` | `decimal(19, 4)` | 我方补贴金额 |
| 139 | `third_subsidy_amt` | `decimal(19, 4)` | 三方补贴金额 |
| 140 | `new_voucher_share_amt` | `decimal(19,4)`* | 优惠分摊金额-新 |
| 141 | `new_company_real_income_share_amt` | `decimal(19,4)`* | 优惠分摊金额(公司实收)-新 |
| 142 | `new_user_pay_money` | `decimal(19,4)`* | 用户实付-新 |

#### K. 金额口径（自营）（22 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 143 | `company_real_income_share_amt` | `decimal(19, 4)` | 优惠分摊金额(公司实收) |
| 144 | `order_cmdty_cnt` | `bigint` | 一单商品数 |
| 145 | `order_category_cnt` | `bigint` | 一单商品数(非周边) |
| 146 | `currency` | `string` | 币种 |
| 147 | `month_exchange_rate` | `decimal(19, 4)` | 对应转换汇率 |
| 148 | `cmdty_sale_cnt` | `bigint` | 商品销量 |
| 149 | `cmdty_origin_amt` | `decimal(19, 4)` | 商品定价 |
| 150 | `addition_amt` | `decimal(19, 4)` | 附属费用 |
| 151 | `cmdty_deal_amt` | `decimal(19, 4)` | 特价优惠金额 优惠金额 |
| 152 | `coupon_amt` | `decimal(19, 4)` | 优惠券抵扣金额 |
| 153 | `cfcoupon_value_amt` | `decimal(19, 4)` | 咖啡库券面值 |
| 154 | `cfcoupon_deal_amt` | `decimal(19, 4)` | 咖啡库券减免金额 |
| 155 | `punch_deduct_amt` | `decimal(19, 4)` | 次数减免金额 |
| 156 | `wx_miniapp_discount_amt` | `decimal(19, 4)` | 微信小程序减免金额 |
| 157 | `coupon_share_amt` | `decimal(19, 4)` | 优惠券分摊金额 |
| 158 | `cfcoupon_share_amt` | `decimal(19, 4)` | 咖啡库券分摊金额 |
| 159 | `punch_income_amt` | `decimal(19, 4)` | 次数收入金额 |
| 160 | `cmdty_payable_amt` | `decimal(19, 4)` | 商品应付价格 |
| 161 | `cmdty_should_amt` | `decimal(19, 4)` | 商品应该付价格,payable_amt减掉优惠券金额 |
| 162 | `cmdty_pay_amt` | `decimal(19, 4)` | 商品实付价格 |
| 163 | `cmdty_income_amt` | `decimal(19, 4)` | 商品收入 |
| 164 | `user_pay_money` | `decimal(19, 4)` | 用户实付 |

---

## 四、口径与使用注意点

| # | 注意点 |
|:-:|:--|
| 1 | **字段重命名陷阱**：`cmdty_income_amt` 在上游取的是 `oc.cmdty_settle_income_amt`（**结算收入**），**不是**同名字段 `cmdty_income_amt`。按「商品收入」口径取数时认这个字段 |
| 2 | **新旧口径并存**：`voucher_share_amt` / `company_real_income_share_amt` / `user_pay_money` 是**旧口径**；`new_*` 三个字段按「券维度窗口 + 定价加权 + 排除周边商品」重算。**用哪个必须先确认**，两者结果不等 |
| 3 | `order_status = 50` 出现在新口径的有效性判断中（主站门店订单状态枚举，**含义待确认**）；不要与电商域的状态枚举（`2/3/7/8/9/10`）混用 |
| 4 | **多币种**：`currency` + `month_exchange_rate`；`new_user_pay_money` 在**抖音**渠道会乘汇率（跨境/三方场景） |
| 5 | **金额分层**：定价（`cmdty_origin_amt`）→ 应付（`cmdty_payable_amt`）→ 应该付（`cmdty_should_amt` = 应付 − 优惠券）→ 实付（`cmdty_pay_amt`）→ 收入（`cmdty_income_amt` = 结算收入）。做优惠/ROI 分析前先定位口径 |
| 6 | **周边商品**（`one_category_name = '周边商品'`）在 `new_*` 口径下分摊额=0，且 `order_category_cnt` 是「非周边商品数」 |
| 7 | 枚举汇总（来自字段注释）：`order_cmdty_situation` 1正常/2损耗/3换货 · `order_type` 外卖/自取/自助 · `exp_disp_type` 1配送人接单/2门店指派（预留） · `pay_from` 微信/支付宝/银联（配置中心） · `group_order` 0普通/1拼单 · `shop_level` 快取店/悠享店/外卖厨房/快闪店/瑞即购/企业内部店/旗舰店 · `coop_pattern` 直营/代理 · `city_tier` 0新一线/1一线/2二线/3三线/4四线 · `cmdty_mode` 现制/外购 · `package_type` 1自营套餐/2渠道套餐 · `package_sub_type` 1预存套餐 · `voucher_type` 1优惠券/2咖啡库券/3阶梯次卡 · `is_custome`/`is_gift` 0否/1是 |
| 8 | **渠道四层 + 三方场域**：`first~fourth_channel_*` 来自两处（`cb` 提供 fourth、`cl` 提供一二三级），做渠道归因时注意字段来源不同表 |

---

## 五、典型 SQL

```sql
-- ① 按一级渠道看订单商品销售（近 7 天）
select first_channel_name,
       count(distinct order_id) as order_cnt,
       sum(cmdty_sale_cnt) as sale_cnt,
       sum(cmdty_income_amt) as income
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_view
where dt between date_sub(current_date(), 7) and date_sub(current_date(), 1)
group by 1
order by income desc

-- ② 营销活动优惠分摊（新旧口径对比，看差异有多大）
select market_name,
       sum(voucher_share_amt) as share_old,
       sum(new_voucher_share_amt) as share_new,
       sum(company_real_income_share_amt) as real_income_old,
       sum(new_company_real_income_share_amt) as real_income_new
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_view
where dt = date_sub(current_date(), 1)
  and voucher_no is not null
group by 1
order by share_new desc

-- ③ 抖音渠道用户实付（含汇率换算）
select dt, third_channel_name, currency,
       sum(user_pay_money) as pay_old,
       sum(new_user_pay_money) as pay_new,
       sum(cmdty_sale_cnt) as sale_cnt
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_view
where dt = date_sub(current_date(), 1)
  and third_channel_name = '抖音'
group by 1,2,3
```

---

## 六、关联

- 索引：[[数据字典索引]] · 分层：[[数据仓库分层说明]]
- **同属门店业务域**：
  - [[dwm_mg_order_cmdty_market_wide_d_inc]] —— 订单商品基础表（**本视图上游 `oc`**，159 字段底座；⚠️ `cmdty_income_amt` 同名陷阱见第三/四节）
  - [[dwm_mg_order_cmdty_channel_bridge_d_inc]] —— 订单商品归属渠道桥接表（**本视图上游 `cb`**）
- **易混淆（务必区分）**：
  - [[dws_eorder_eorder_commodity_d_his_combine]] —— 电商商城（即享）订单商品，**非门店**
  - [[dws_eorder_eorder_d_his_combine]] —— 电商商城订单头

---

## 七、上游字典（4 张全部已建 ✅）

| 来源表 | 角色 | 优先级 |
|:--|:--|:--|
| [[dwm_mg_order_cmdty_market_wide_d_inc]] | 主表（增量），159 字段底座；本视图 148 字段取自它 | ✅ **已建字典**（2026-10-12，↓ 本文档类型即由它回填） |
| [[dwm_mg_order_cmdty_channel_bridge_d_inc]] | 渠道桥（fourth_channel / third_site_channel） | ✅ **已建字典**（2026-10-12） |
| [[dim_channel_level_d_his]] | 渠道层级维（一~四级渠道） | ✅ **已建字典**（2026-10-12，本文档 7 个渠道字段类型由它回填） |
| [[dim_sku_ord_rmk_d_a]] | 订单商品属性维（杯型/温度 等 44 属性） | ✅ **已建字典**（2026-10-12） |

> **类型已回填 164/164（全覆盖）**；4 张上游表字典**全部建成**（主表 / 渠道桥 / 渠道层级维 / 商品属性维）。
