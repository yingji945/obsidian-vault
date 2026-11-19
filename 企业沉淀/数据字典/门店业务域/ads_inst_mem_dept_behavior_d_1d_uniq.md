---
created: 2026-11-18
updated: 2026-11-18
tags: [企业, 数据字典, 门店业务域, ADS, 即享, 门店行为]
field_status: 🔴 部分（字段名来自用户 SQL 引用，**未获 DDL**；数量约 26，类型全部未知）
source: 用户 SQL 引用 2026-11-18（多段查询中出现的字段）；**待 DDL 核定**
---

# dw_drs_ads.ads_inst_mem_dept_behavior_d_1d_uniq

> **ADS 应用层 · 即享咖啡会员门店行为与订单日标签宽表** —— 日 × 人 × **门店**粒度，把即享菜单曝光、点击、加购、下单、支付压在一行，并带门店与渠道属性
> 粒度：1 行 = 1 人 1 天 1 门店 · 库：`dw_drs_ads` · **引擎：Doris**

> 🔴 **本篇是「从使用中反推」的草稿字典。** 字段清单来自你多段 SQL 里实际引用到的字段，**没有拿到 DDL**，字段总数、类型、完整字段集都可能不全。拿到 DDL 后请按 [[数据字典维护规范]] 更新本页并把 `field_status` 改为 ✅。

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_drs_ads.ads_inst_mem_dept_behavior_d_1d_uniq` |
| 库 / 层级 | `dw_drs_ads` / **ADS 应用层**（`_1d` 日粒度 + `uniq` 已去重） |
| 业务域 | **门店业务域**（数据由门店侧即享业务抽离而来） |
| 角色 | **门店级即享行为 + 交易标签宽表**：既有曝光点击（`is_menu_page_bw` / `is_inst_menu_ck`），又有交易标识（`is_inst_ord_mem` / `is_inst_ord_pay_mem`）和金额，同时带 **渠道与门店属性** |
| 粒度 | 日 × 人 × **门店**（`dt` + `mem_id` + `dept_id`） |
| **引擎** | 🔴 **Doris**（Hive 下报 `Table or view not found`） |

**与 `cmdty` 版的核心差异**：本表有**渠道、城市、门店**三个维度字段，因此它是**限定分析范围的那个人群池**；`cmdty` 版负责商品级行为。

---

## 二、同族表对照

| 表 | 维度 | 字段数 | 独有能力 |
|:--|:--|--:|:--|
| **`ads_inst_mem_dept_behavior_d_1d_uniq`（本表）** | 日 × 人 × **门店** | 约 26 | ✅ **渠道过滤**（`first_channel_name` / `third_channel_name`）、城市（`city_name`）、即享售卖门店（`is_inst_sale_shop`）|
| `ads_inst_mem_cmdty_behavior_d_1d_uniq` | 日 × 人 × **商品** | 18 | ✅ 商品级漏斗（`cmdty_code`、卡片点击、加购、结算）；🔴 无渠道/城市/门店字段 |

### 🔴 三个同名不同义的字段（最易踩）

| 字段 | 本表（`dept` 版）| `cmdty` 版 |
|:--|:--|:--|
| `is_inst_ord_mem` | **人级**：此人当日是否有即享订单（含未支付）| **商品行级**：此人当日是否下了**这个商品** |
| `inst_ord_cmdty_income_pay_amt` | **即享订单整单金额**（可能含非即享商品）| 按订单内已支付即享商品行数**分摊到本商品行** |
| `inst_cmdty_income_pay_amt` | 人级即享**品类**金额（干净口径）| 该商品行的即享品类金额 |

---

## 三、字段清单（反推草稿 · 待 DDL 核定）

> 下列字段均来自你实际 SQL 中的引用。**类型一律未知**，分组是按语义推测的。

### A. 主键与维度（7 字段）

| # | 字段名 | 语义 |
|:-:|:------|:-----|
| 1 | `dt` | 日期 |
| 2 | `mem_id` | 会员 ID |
| 3 | `dept_id` | 门店部门 ID |
| 4 | `city_id` | 城市 ID |
| 5 | `city_name` | 城市名称 |
| 6 | `shop_name` | 门店名称 |
| 7 | `shop_level` | 门店层级（快取店 / 悠享店等）|

### B. 渠道与门店属性（5 字段）

| # | 字段名 | 语义 |
|:-:|:------|:-----|
| 8 | `first_channel_name` | **一级渠道名称**（如 `私域`）|
| 9 | `third_channel_name` | **三级渠道名称**（如 `app/微信小程序`）|
| 10 | `shop_type_name` | 门店类型名称 |
| 11 | `is_inst_sale_shop` | 是否**即享售卖门店**（1是 0否）|
| 12 | `order_type` | 订单类型（外卖订单 / 自取订单 / 自助订单）|

### C. 行为标识（9 字段）

| # | 字段名 | 语义 |
|:-:|:------|:-----|
| 13 | `is_start_mem` | 是否启动 App/小程序 |
| 14 | `is_main_page_bw` | 是否**首页曝光** |
| 15 | `is_menu_page_bw` | 是否**菜单页曝光** |
| 16 | `is_inst_menu_bw` | 是否**即享咖啡菜单曝光** |
| 17 | `is_inst_menu_ck` | 是否**即享咖啡菜单点击** |
| 18 | `is_inst_productdetail_bw` | 是否**即享商品详情页曝光** |
| 19 | `is_productdetail_bw` | 是否**商品详情页曝光**（全品类）|
| 20 | `is_mem_menu_cmdty_addcart_ck` | 是否**菜单商品加购**点击 |
| 21 | `is_mem_order_confirm_bw` | 是否**订单确认页曝光** |

### D. 交易标识与金额（5 字段）

| # | 字段名 | 语义 |
|:-:|:------|:-----|
| 22 | `is_ord_pay_mem` | 是否**有支付订单**（全品类）|
| 23 | `is_inst_ord_mem` | 是否**有即享咖啡订单**（**订单级，含未支付**，混合订单也置 1）|
| 24 | `is_inst_ord_pay_mem` | 是否**有即享咖啡支付订单** |
| 25 | `inst_ord_cmdty_income_pay_amt` | 即享**订单整单**金额（可能含非即享商品）|
| 26 | `inst_cmdty_income_pay_amt` | 即享**品类商品**金额（✅ 推荐用这个）|
| — | `cmdty_income_pay_amt` | 全品类商品金额（在 SQL 中出现，语义按名称判断）|

> ⚠️ 上表共 26 个具名字段 + 1 个 `cmdty_income_pay_amt` = 27 个候选项。**真实字段集与总数以 DDL 为准。**

---

## 四、使用注意点（六条）

### ① 引擎是 Doris

```sql
-- ✅ Doris 引擎；Hive 下报 Table or view not found
select 1 from dw_drs_ads.ads_inst_mem_dept_behavior_d_1d_uniq limit 0
```

### ② 渠道过滤会清空曝光数据 —— 必须 LEFT JOIN

只有**私域资源位**才产生曝光点击记录。把 `first_channel_name = '私域'` 和 `third_channel_name = 'app/微信小程序'` 压进同一个 WHERE，曝光人数会归零或断崖，而订单侧照常有数 —— 表面像「曝光极低、转化极高」。

**标准结构**：

```sql
exposure 侧：只按 城市 / 门店属性 / 日期 筛，不加渠道
order     侧：加渠道过滤
两段各自按 dt + mem_id 取人，再 left join
```

### ③ `is_inst_ord_mem` 是订单级，不是品类级

只要订单里有即享商品就置 1，**混合订单也算**。用它数「即享买家」人数会偏大。

- **订单级**：`is_inst_ord_mem`（含混合单，口径宽）
- **品类级金额**：`inst_cmdty_income_pay_amt`（只算即享商品本身，✅ 推荐）
- **整单金额**：`inst_ord_cmdty_income_pay_amt`（可能含其他商品）

**验证混合单占比**：

```sql
case when abs(coalesce(inst_ord_cmdty_income_pay_amt, 0)
           - coalesce(inst_cmdty_income_pay_amt, 0)) < 0.01
     then 'A. 纯即享订单' else 'B. 混合订单' end as 订单类型
, count(distinct if(is_inst_ord_mem = 1, mem_id, null)) as 人数
```

**实测基线**（2026-11-05，广州+杭州，`is_inst_sale_shop = 1`）：`inst_cmdty_income_pay_amt` 3,411.58 元 vs `inst_ord_cmdty_income_pay_amt` 8,655.82 元 —— **61% 的钱花在非即享商品上**，混合单普遍存在。

### ④ 人天先压平再判断

一行是「人 × 日 × 门店」，同一个人多天/多门店会有多行。算**人数**用 `count(distinct mem_id)`；算**周期去重人数**要先按 `mem_id` 聚合。

```sql
-- 按天看一眼
select dt, count(distinct if(is_inst_menu_bw = 1, mem_id, null)) as 曝光人数 ...
-- 周期去重
with p as (select mem_id, max(is_inst_menu_bw) as bw ... group by mem_id)
```

### ⑤ 严格漏斗要累积条件

各级独立 `count(distinct if(flag=1, ...))` 会出现「下单人数 > 点击人数」。必须：

```sql
count(distinct if(is_inst_menu_bw = 1 and is_inst_menu_ck = 1
                  and is_inst_productdetail_bw = 1 and is_inst_ord_pay_mem = 1
                 , mem_id, null))
```

### ⑥ 和 `cmdty` 版联用时的分工

| 要什么 | 用哪张 |
|:--|:--|
| 限定城市 / 门店 / 渠道 | **本表**（`dept` 版）|
| 商品级行为（曝光→点击→卡片点击→加购→结算→下单）| `cmdty` 版 |
| 人级整体即享行为（不区分商品）| 本表 |

**联用模板**：本表筛人群池 → 按 `dt + mem_id` left join `cmdty` 版的行为 → 曝光侧不加人群池条件，下单侧加。

---

## 五、待补事项

| # | 待补 | 怎么补 |
|:-:|:--|:--|
| 1 | **完整 DDL**（字段全集 + 类型）| Doris 引擎下 `SHOW CREATE TABLE dw_drs_ads.ads_inst_mem_dept_behavior_d_1d_uniq`（注意：平台只支持 select/with/explain，`show` 可能不可用，需从元数据平台取）|
| 2 | **字段总数确认** | 当前反推 26~27 个，需核定 |
| 3 | **`cmdty_income_pay_amt` 的定位** | 是全品类人级金额，还是本表实际不存在该字段？|
| 4 | **`order_type` / `shop_level` 枚举** | 枚举值未知 |

---

> 关联：[[数据字典索引]] · [[ads_inst_mem_cmdty_behavior_d_1d_uniq]] · [[SQL经验库]] · [[门店即享复购分析SQL模板]] · [[门店即享渠道价值评估-SP4386]]
