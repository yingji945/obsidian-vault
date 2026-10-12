---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 订单交易域, 门店订单, DWM, 主表]
field_status: ✅ 完整（159 字段含类型，来源 SHOW CREATE TABLE）
source: 用户提供 CREATE TABLE（2026-10-12）；DDL last_modified 2026-09-14
---

# dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc

> **订单商品基础 dwm 表** —— 门店订单商品行**字段最全的主表**（含本位币、结算收入、配送费退款）
> 粒度：1 行 = 1 个订单商品（`order_cmdty_id`）· 分区：`dt`（**string**）· 字段数：**159**

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc` |
| 业务域 | **订单交易域**（门店业务） |
| 角色 | **数据底座**：订单交易域最全的订单商品明细（下游视图从它取 148 个字段） |
| 粒度 | 订单商品行（1 订单商品 = 1 行） |
| 层级 | `DWM`（日增量 `_inc`） |
| 分区键 | `dt`（string，日期分区） |
| 字段数 | 159（12 组，见第三节） |
| 存储 | ORC + ZLIB |
| 最近变更 | 2026-09-14（DDL `last_modified_time`） |

---

## 二、它在血缘里的位置 ⭐

```
dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc     ← 本表（订单商品基础，159 字段）
        │  join on dt + order_cmdty_id
        ├──► dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc   渠道桥
        ├──► dw_dim.dim_channel_level_d_his                    渠道层级维（一二三级渠道）
        ├──► dw_dim.dim_sku_ord_rmk_d_a                        SKU 备注（杯型/温度）
        ▼
dw_dwm.dwm_mg_order_cmdty_market_wide_d_view   订单商品渠道归因视图（下游，164 字段）
```

> 本表**不含渠道归因字段**——`first~fourth_channel_*` / `third_site_channel_*` 全部由渠道桥 + 渠道层级维补足。
> 本表也**不含杯型/温度**（`cup_rmk_name` / `temp_rmk_name` 来自 SKU 备注维）。

---

## 三、⚠️ 与下游视图的口径差异（最容易算错的地方）

下游视图 [[dwm_mg_order_cmdty_market_wide_d_view]] 从本表取 148 字段，但**改名 1 个、丢弃 11 个**：

### 3.1 同名陷阱（最高危）🔴

本表**同时有两个**金额字段：

| 本表字段 | 含义 | 下游视图 |
|:--|:--|:--|
| `cmdty_income_amt` | **商品收入**（原口径） | ❌ **未暴露** |
| `cmdty_settle_income_amt` | 商品结算价收入 | ✅ 暴露，但**改名为 `cmdty_income_amt`** |

> 后果：**视图里的 `cmdty_income_amt` 实际是「结算价收入」**，不是本表的「商品收入」。
> 需要原始「商品收入」口径时**必须回到本表**取 `cmdty_income_amt`；两者数值不等，混用会出现"同一指标两个数"。

### 3.2 视图拿不到的 11 个字段

| 类别 | 字段 | 用途 |
|:--|:--|:--|
| **本位币（9 个）** | `addition_amt_local`、`cmdty_income_local`、`cmdty_origin_amt_local`、`cmdty_pay_amt_local`、`cmdty_settle_income_amt_local`、`delivery_income_amt_local`、`delivery_pay_share_amt_local`、`delivery_refund_amt_local`、`user_pay_amt_local` | **多币种/汇率归一分析必须回本表**（视图只给原币） |
| **配送费退款（2 个）** | `delivery_refund_amt`、`delivery_refund_amt_local` | 配送费退款分摊口径 |

---

## 四、字段清单（159 字段 · 12 组）

> 全部含类型（来源 SHOW CREATE TABLE）。

#### A. 主键与订单标识（13 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `order_cmdty_id` | `bigint` | 订单商品ID |
| 2 | `order_id` | `bigint` | 订单ID |
| 3 | `order_no` | `string` | 订单编号 |
| 4 | `mem_id` | `bigint` | 会员id |
| 5 | `dept_id` | `bigint` | 部门id |
| 6 | `order_status` | `int` | 订单状态 |
| 7 | `order_origin` | `int` | 订单来源 |
| 8 | `order_channel` | `int` | 订单渠道 |
| 9 | `order_type` | `int` | 订单类型:外卖订单/自取订单/ 自助订单 |
| 10 | `actual_order_type` | `int` | 实际订单类型 |
| 11 | `order_cmdty_situation` | `int` | 商品情况 参见枚举 1正常 2损耗 3换货 |
| 12 | `third_order_id` | `bigint` | 三方渠道订单ID |
| 13 | `third_order_no` | `string` | 三方渠道订单编号 |

#### B. 时间戳（12 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 14 | `order_create_time` | `timestamp` | 订单创建时间 |
| 15 | `order_update_time` | `timestamp` | 订单修改时间 |
| 16 | `order_pay_time` | `timestamp` | 订单支付时间 |
| 17 | `order_finish_time` | `timestamp` | 订单完成时间 |
| 18 | `product_accept_time` | `timestamp` | 接单时间（开始制作时间） |
| 19 | `product_finish_time` | `timestamp` | 制作完成时间 |
| 20 | `exp_getit_time` | `timestamp` | 取餐时间 |
| 21 | `exp_finish_time` | `timestamp` | 配送完成时间 |
| 22 | `retain_interval_time` | `int` | 保鲜时段 |
| 23 | `refund_time` | `timestamp` | 退款时间 |
| 24 | `set_up_time` | `timestamp` | 开业时间 |
| 25 | `commodity_actual_launch_date` | `string` | 上市时间 |

#### C. 履约与配送（8 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 26 | `exp_getit_type` | `int` | 取餐方式 |
| 27 | `exp_disp_type` | `int` | 接单类型(预留字段)（1-配送人接单、2-门店指派） |
| 28 | `time_slice_half_hour` | `string` | 半小时时段 |
| 29 | `supplier_id` | `int` | 配送商id |
| 30 | `supplier_no` | `string` | 配送商编号 |
| 31 | `supplier_name` | `string` | 配送商名称 |
| 32 | `supplier_type` | `int` | 配送商类型 |
| 33 | `exp_distance` | `decimal(19, 4)` | 配送距离 |

#### D. 状态与标记（10 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 34 | `pay_from` | `int` | 支付方式（微信、支付宝、银联，来源：配置中心） |
| 35 | `group_order` | `int` | 拼单类型（0-普通，1-拼单） |
| 36 | `income_status` | `int` | 商品收入状态 |
| 37 | `invoice_status` | `int` | 商品开票状态 |
| 38 | `refund_status` | `int` | 商品退款状态 |
| 39 | `refund_origin` | `int` | 退款来源 1自动2人工 |
| 40 | `is_custome` | `int` | 是否客制化0否1是 |
| 41 | `is_gift` | `int` | 是否是赠送商品0否1是 |
| 42 | `is_99_coupon` | `int` | 是否使用99券 |
| 43 | `is_multi_cup` | `int` | 是否一单多杯 |

#### E. 门店与区域（17 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 44 | `shop_id` | `bigint` | 门店id |
| 45 | `shop_no` | `string` | 门店编号 |
| 46 | `shop_name` | `string` | 门店名称 |
| 47 | `shop_type` | `int` | 门店类型 |
| 48 | `shop_level` | `int` | 门店层级:快取店/悠享店/外卖厨房/快闪店/瑞即购/企业内部店/旗舰店 |
| 49 | `shop_price_level` | `bigint` | 商品价位级别 |
| 50 | `coop_pattern_code` | `string` | 运营合作模式主数据编号：直营，代理 |
| 51 | `coop_pattern_name` | `string` | 运营合作模式名称：直营，代理 |
| 52 | `area_id` | `bigint` | 区域ID |
| 53 | `area_name` | `string` | 区域 |
| 54 | `city_id` | `bigint` | 城市ID |
| 55 | `city_name` | `string` | 城市 |
| 56 | `city_tier` | `int` | 城市等级 0 新一线 1 一线 2 二线 3 三线 4 四线 |
| 57 | `prov_id` | `bigint` | 省份id |
| 58 | `prov_name` | `string` | 省份 |
| 59 | `business_region_code` | `string` | 经营区域code |
| 60 | `business_region_name` | `string` | 经营区域名称 |

#### F. 商品与 SKU（18 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 61 | `cmdty_id` | `bigint` | 商品ID |
| 62 | `cmdty_sale_id` | `bigint` | 商品销售ID |
| 63 | `cmdty_sale_plan_id` | `bigint` | 商品销售方案ID |
| 64 | `cmdty_sale_unit` | `int` | 商品销售单位 |
| 65 | `cmdty_code` | `string` | 商品编号 |
| 66 | `cmdty_name` | `string` | 商品名称 |
| 67 | `cmdty_size` | `string` | 商品大小 |
| 68 | `cmdty_temper` | `string` | 商品冷热属性 |
| 69 | `cmdty_mode` | `int` | 商品类型 参见枚举 现制商品 外购商品 |
| 70 | `one_category_name` | `string` | 商品一级分类名称 |
| 71 | `two_category_name` | `string` | 商品二级分类名称 |
| 72 | `three_category_name` | `string` | 商品三级分类名称 |
| 73 | `cmdty_theme` | `string` | 商品主题 |
| 74 | `cmdty_series` | `string` | 商品系列 |
| 75 | `cmdty_texture` | `string` | 商品浓度 |
| 76 | `sku_code` | `string` | sku编码 |
| 77 | `sku_name` | `string` | sku名称 |
| 78 | `business_cmdty_name` | `string` | 业务商品名称，若无业务商品，则为商品名称 |

#### G. 套餐（6 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 79 | `package_id` | `bigint` | 商品系统套餐ID |
| 80 | `package_code` | `string` | 商品系统套餐CODE |
| 81 | `package_name` | `string` | 商品系统套餐NAME |
| 82 | `package_batch_no` | `int` | 批次号 套餐多份时展示使用  |
| 83 | `package_type` | `int` | 套餐类型(1为自营套餐，2为渠道套餐) |
| 84 | `package_sub_type` | `int` | 套餐子类型 1 预存套餐 |

#### H. 营销与优惠（31 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 85 | `market_id` | `bigint` | 营销活动ID |
| 86 | `market_name` | `string` | 营销活动名称 |
| 87 | `market_type` | `int` | 营销活动类型 |
| 88 | `market_sub_type` | `int` | 营销活动子类型 |
| 89 | `company_discount_type` | `int` | 企业优惠类型 |
| 90 | `company_discount_id` | `bigint` | 企业优惠id |
| 91 | `company_discount_name` | `string` | 企业优惠名称 |
| 92 | `voucher_id` | `bigint` | 优惠id |
| 93 | `voucher_no` | `string` | 优惠编号 |
| 94 | `voucher_type` | `int` | 优惠类型 1优惠券 2咖啡库券 3阶梯次卡 |
| 95 | `voucher_origin` | `int` | 优惠来源 |
| 96 | `voucher_status` | `int` | 优惠状态 |
| 97 | `template_id` | `bigint` | 优惠模板id |
| 98 | `template_name` | `string` | 优惠模板名称 |
| 99 | `template_type` | `int` | 优惠模板类别 |
| 100 | `proposal_id` | `bigint` | 优惠方案ID |
| 101 | `proposal_no` | `string` | 优惠方案编号 |
| 102 | `proposal_name` | `string` | 优惠方案名称 |
| 103 | `proposal_type_name` | `string` | 优惠方案类型名称 |
| 104 | `proposal_sub_type_name` | `string` | 优惠方案子类型名称 |
| 105 | `discount_type` | `int` | 打折类型 |
| 106 | `discount_sub_type` | `int` | 打折子类型 |
| 107 | `allowance_project_id` | `bigint` | 一级补贴项目ID |
| 108 | `allowance_project_no` | `string` | 一级补贴项目编号 |
| 109 | `allowance_project_name` | `string` | 一级补贴项目名称 |
| 110 | `sub_allowance_project_id` | `bigint` | 二级补贴项目ID |
| 111 | `sub_allowance_project_no` | `string` | 二级补贴项目编号 |
| 112 | `sub_allowance_project_name` | `string` | 二级补贴项目名称 |
| 113 | `voucher_share_amt` | `decimal(19, 4)` | 分摊金额 |
| 114 | `market_amt` | `decimal(19, 4)` | 营销活动优惠价格 |
| 115 | `company_discount_amt` | `decimal(19, 4)` | 企业减免金额 |

#### I. 金额（自营原币）（21 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 116 | `company_real_income_share_amt` | `decimal(19, 4)` | 公司分摊实收金额 |
| 117 | `cmdty_origin_amt` | `decimal(19, 4)` | 商品定价 |
| 118 | `addition_amt` | `decimal(19, 4)` | 附属费用 |
| 119 | `cmdty_deal_amt` | `decimal(19, 4)` | 特价优惠金额 优惠金额 |
| 120 | `coupon_amt` | `decimal(19, 4)` | 优惠券抵扣金额 |
| 121 | `cfcoupon_value_amt` | `decimal(19, 4)` | 咖啡库券面值 |
| 122 | `cfcoupon_deal_amt` | `decimal(19, 4)` | 咖啡库券减免金额 |
| 123 | `punch_deduct_amt` | `decimal(19, 4)` | 次数减免金额 |
| 124 | `wx_miniapp_discount_amt` | `decimal(19, 4)` | 微信小程序减免金额 |
| 125 | `coupon_share_amt` | `decimal(19, 4)` | 优惠券分摊金额 |
| 126 | `cfcoupon_share_amt` | `decimal(19, 4)` | 咖啡库券分摊金额 |
| 127 | `punch_income_amt` | `decimal(19, 4)` | 次数收入金额 |
| 128 | `cmdty_payable_amt` | `decimal(19, 4)` | 商品应付价格 |
| 129 | `cmdty_should_amt` | `decimal(19, 4)` | 商品应该付价格,payable_amt减掉优惠券金额 |
| 130 | `cmdty_pay_amt` | `decimal(19, 4)` | 商品实付价格 |
| 131 | `cmdty_income_amt` | `decimal(19, 4)` | 商品收入 |
| 132 | `cmdty_settle_income_amt` | `decimal(19, 4)` | 商品结算价收入 |
| 133 | `delivery_income_amt` | `decimal(19, 4)` | 配送费收入(非周边商品分摊) |
| 134 | `user_pay_money` | `decimal(19, 4)` | 用户实付 |
| 135 | `delivery_pay_share_amt` | `decimal(19, 4)` | 配送费实付分摊金额 |
| 136 | `delivery_refund_amt` | `decimal(19, 4)` | 配送费退款分摊金额 |

#### J. 三方金额与补贴（9 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 137 | `third_discnt_amt` | `decimal(19, 4)` | 三方商品折扣后金额 |
| 138 | `third_mkt_amt` | `decimal(19, 4)` | 三方其他商品减免金额 |
| 139 | `third_pay_amt` | `decimal(19, 4)` | 三方用户实付 |
| 140 | `third_red_packet_amt` | `decimal(19, 4)` | 三方红包分摊金额 |
| 141 | `third_packing_charge_amt` | `decimal(19, 4)` | 三方打包费 |
| 142 | `third_allowance_share_amt` | `decimal(19, 4)` | 三方补贴分摊至商品 |
| 143 | `total_subsidy_amt` | `decimal(19, 4)` | 总补贴金额 |
| 144 | `luckin_subsidy_amt` | `decimal(19, 4)` | 我方补贴金额 |
| 145 | `third_subsidy_amt` | `decimal(19, 4)` | 三方补贴金额 |

#### K. 金额（本位币 · ⚠️视图未暴露）（9 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 146 | `delivery_pay_share_amt_local` | `decimal(19, 4)` | 配送费实付分摊金额_本位币 |
| 147 | `delivery_income_amt_local` | `decimal(19, 4)` | 配送费收入分摊_本位币 |
| 148 | `cmdty_origin_amt_local` | `decimal(19, 4)` | 商品定价_本位币 |
| 149 | `addition_amt_local` | `decimal(19, 4)` | 附属费用_本位币 |
| 150 | `cmdty_pay_amt_local` | `decimal(19, 4)` | 商品实付价格_本位币 |
| 151 | `cmdty_income_local` | `decimal(19, 4)` | 商品收入_本位币 |
| 152 | `cmdty_settle_income_amt_local` | `decimal(19, 4)` | 商品结算价收入_本位币 |
| 153 | `user_pay_amt_local` | `decimal(19, 4)` | 用户实付_本位币 |
| 154 | `delivery_refund_amt_local` | `decimal(19, 4)` | 配送费退款分摊金额_本位币 |

#### L. 计数与币种（5 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 155 | `order_cmdty_cnt` | `bigint` | 一单商品数 |
| 156 | `order_category_cnt` | `bigint` | 一单商品数(非周边) |
| 157 | `currency` | `string` | 币种 |
| 158 | `month_exchange_rate` | `decimal(19, 4)` | 对应转换汇率 |
| 159 | `cmdty_sale_cnt` | `bigint` | 商品销量 |

---

## 五、口径与使用注意点

| # | 注意点 |
|:-:|:--|
| 1 | **`order_status` 是 int，但 DDL 未给枚举含义** ⚠️。已知下游视图的新口径判断里用了 `order_status = 50`（含义仍待确认）。**不要与电商域（`eorder_status` 的 2/3/7/8/9/10）混用** |
| 2 | **金额分层**：定价（`cmdty_origin_amt`）→ 应付（`cmdty_payable_amt`）→ 应该付（`cmdty_should_amt` = 应付 − 优惠券）→ 实付（`cmdty_pay_amt`）→ 收入（`cmdty_income_amt`）/ 结算收入（`cmdty_settle_income_amt`）。做优惠/ROI 前先定位口径 |
| 3 | **原币 vs 本位币并存**：`*_local` 后缀 = 本位币；带 `currency` + `month_exchange_rate` 支持多币种（抖音等三方场域） |
| 4 | **周边商品**：`one_category_name = '周边商品'` 在优惠分摊口径里被排除；`order_category_cnt` 是「非周边商品数」 |
| 5 | **关联键**：`dt + order_cmdty_id`（订单商品行粒度，一单多商品多行）；`order_id` 是订单粒度，**去重统计用 `count(distinct order_id)`** |
| 6 | 增量表（`_inc`）：每天只写当天分区；跨天分析按 `dt` 范围扫多分区 |
| 7 | 枚举汇总（DDL 注释）：`order_cmdty_situation` 1正常/2损耗/3换货 · `order_type` 外卖/自取/自助 · `exp_disp_type` 1配送人接单/2门店指派（预留） · `pay_from` 微信/支付宝/银联 · `group_order` 0普通/1拼单 · `shop_level` 快取店/悠享店/外卖厨房/快闪店/瑞即购/企业内部店/旗舰店 · `coop_pattern` 直营/代理 · `city_tier` 0新一线/1一线/2二线/3三线/4四线 · `cmdty_mode` 现制/外购 · `package_type` 1自营/2渠道 · `package_sub_type` 1预存套餐 · `voucher_type` 1优惠券/2咖啡库券/3阶梯次卡 · `is_custome`/`is_gift` 0否/1是 · `refund_origin` 1自动/2人工 |

---

## 六、典型 SQL

```sql
-- ① 门店订单商品收入 vs 结算收入（两个口径差多少）
select dt,
       sum(cmdty_income_amt)         as income_gross,      -- 商品收入（原口径）
       sum(cmdty_settle_income_amt)  as income_settle,     -- 商品结算价收入
       sum(cmdty_income_amt) - sum(cmdty_settle_income_amt) as diff
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc
where dt = date_sub(current_date(), 1)
group by dt

-- ② 多币种订单（本位币 vs 原币）
select currency, month_exchange_rate,
       count(distinct order_id) as order_cnt,
       sum(user_pay_money)        as pay_original,
       sum(user_pay_amt_local)    as pay_local
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc
where dt = date_sub(current_date(), 1)
  and currency is not null and currency <> 'CNY'
group by 1,2
order by order_cnt desc

-- ③ 门店 × 商品分类的销售（按订单去重）
select shop_level, one_category_name,
       count(distinct order_id)   as order_cnt,
       count(distinct order_cmdty_id) as cmdty_cnt,
       sum(cmdty_sale_cnt)        as sale_cnt,
       sum(cmdty_settle_income_amt) as income
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc
where dt = date_sub(current_date(), 1)
  and order_cmdty_situation = 1        -- 排除损耗/换货
group by 1,2
order by income desc
```

---

## 七、关联

- 索引：[[数据字典索引]] · 分层：[[数据仓库分层说明]]
- **下游（本表喂它）**：[[dwm_mg_order_cmdty_market_wide_d_view]] —— 订单商品渠道归因视图（本表是其 `oc`）
- **下游的桥接**：[[dwm_mg_order_cmdty_channel_bridge_d_inc]] —— 订单商品归属渠道桥接表（本表的兄弟表，同粒度）
- **易混淆**：[[dws_eorder_eorder_commodity_d_his_combine]]（**即享商城**电商订单商品，非门店）

---

## 八、待补

| 对象 | 说明 |
|:--|:--|
| `order_status` 枚举 | ⚠️ DDL 未给含义。**找数仓/开发要状态字典**（下游视图用了 `= 50`） |
| [[dim_channel_level_d_his]] | 渠道层级维（一~四级渠道 id/name） | ✅ **已建字典**（2026-10-12） |
| `dw_dim.dim_sku_ord_rmk_d_a` | SKU 备注维（杯型/温度），**未建字典** |
