---
created: 2026-11-18
updated: 2026-11-18
tags: [企业, 数据字典, 门店业务域, ADS, 即享, 商品行为]
field_status: 🟡 字段名与语义完整（18/18）；**类型未核定**（用户提供的是 DDL 注释清单，非 SHOW CREATE TABLE）
source: 用户提供 DDL 注释 2026-11-18
---

# dw_drs_ads.ads_inst_mem_cmdty_behavior_d_1d_uniq

> **ADS 应用层 · 即享咖啡会员商品行为与订单日标签宽表** —— 日 × 人 × **商品**粒度，把即享商品的曝光、点击、加购、商详、结算、下单、支付全链路行为压在一行
> 粒度：1 行 = 1 人 1 天 1 商品 · 库：`dw_drs_ads` · 字段数：**18** · **引擎：Doris**

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_drs_ads.ads_inst_mem_cmdty_behavior_d_1d_uniq` |
| 库 / 层级 | `dw_drs_ads` / **ADS 应用层**（`_1d` 日粒度 + `uniq` 已去重） |
| 业务域 | **门店业务域**（数据由门店侧即享业务抽离而来） |
| 角色 | **商品级即享行为 + 交易标签宽表**：同一行既有行为标识（`is_mem_menu_cmdty_bw` 曝光 / `is_mem_menu_cmdty_ck` 点击）又有交易标识（`is_inst_ord_mem` 下单 / `is_inst_ord_pay_mem` 支付）和金额 |
| 粒度 | 日 × 人 × **商品**（`dt` + `mem_id` + `cmdty_code`） |
| 字段数 | 18（4 组，见第三节） |
| **引擎** | 🔴 **Doris**（Hive 查不到，报 `Table or view not found`） |

---

## 二、同族表对照（重要）

同前缀有**两张**表，粒度不同，**不能混用字段语义**：

| 表 | 维度 | 字段数 | 主键 | 有渠道/城市/门店字段吗 |
|:--|:--|--:|:--|:--|
| `ads_inst_mem_**dept**_behavior_d_1d_uniq` | 日 × 人 × **门店** | 26 | `dt` + `mem_id` + `dept_id` | ✅ 有 `first_channel_name` / `third_channel_name` / `city_name` / `is_inst_sale_shop` |
| **`ads_inst_mem_cmdty_behavior_d_1d_uniq`（本表）** | 日 × 人 × **商品** | **18** | `dt` + `mem_id` + `cmdty_code` | 🔴 **全都没有** |

**这意味着本表无法独立筛选城市、门店、渠道。** 要做「广州+杭州 / 私域小程序」这类限定，必须用 `dept` 版筛人群池，再按 `dt + mem_id` left join 过来。

> ⚠️ **三个同名字段含义不同**（最易踩的坑）：
> | 字段 | `dept` 版 | 本表（`cmdty` 版）|
> |:--|:--|:--|
> | `is_inst_ord_mem` | **人级**：此人当日是否有即享订单 | **商品行级**：此人当日是否下了**这个商品** |
> | `inst_ord_cmdty_income_pay_amt` | **整单金额**（含非即享商品）| **按订单内已支付即享商品行数分摊到本商品行** |
> | `inst_cmdty_income_pay_amt` | 人级即享品类金额 | 该商品行的即享品类金额 |

---

## 三、字段清单（18 字段 · 4 组）

### A. 主键与维度（3 字段）

| # | 字段名 | 说明 |
|:-:|:------|:-----|
| 1 | `dt` | 日期 |
| 2 | `mem_id` | 会员 ID |
| 3 | `cmdty_code` | 商品编号（本表的商品粒度键）|

### B. 商品属性（1 字段）

| # | 字段名 | 说明 |
|:-:|:------|:-----|
| 4 | `cmdty_name` | 商品名称 |

### C. 行为标识（商品级漏斗 · 9 字段）

| # | 字段名 | 说明 |
|:-:|:------|:-----|
| 5 | `is_mem_menu_cmdty_bw` | 是否**曝光**菜单即享咖啡商品（1是 0否）|
| 6 | `is_mem_menu_cmdty_ck` | 是否**点击**菜单即享咖啡商品 |
| 7 | `is_mem_menu_cmdty_cmdty_ck` | **商品卡片点击商品**（`ck_type=1`）|
| 8 | `is_mem_menu_cmdty_addcart_ck` | **商品卡片加购按钮点击**（`ck_type=2`）|
| 9 | `is_mem_cmdty_add_cart` | 是否**加购**即享咖啡商品 |
| 10 | `is_inst_productdetail_bw` | **商品详情页曝光** |
| 11 | `is_mem_cmdty_buy_ck` | **商详页立即购买**点击 |
| 12 | `is_mem_shoppingcart_billing_ck` | **购物车去结算**点击（按 `prop_data.goods[].spu_code` 归因）|
| 13 | `is_mem_order_confirm_bw` | **订单确认页商品曝光**（`confirmorder_cmdty_bw` + `prop_data.cmdty_id`）|

> **标准商品级漏斗链**：曝光(5) → 点击(6) → 卡片点击(7) → 商详曝光(10) → 立即购买(11) → 结算(12) → 下单/支付(14/15)

### D. 交易标识与金额（5 字段）

| # | 字段名 | 说明 |
|:-:|:------|:-----|
| 14 | `is_inst_ord_mem` | 当日**该商品**是否有下单（**不限订单状态**，含未支付/取消）|
| 15 | `is_inst_ord_pay_mem` | 当日**该商品**是否有支付订单 |
| 16 | `inst_ord_cmdty_income_pay_amt` | 当日含即享咖啡订单支付总额，**按订单内已支付即享商品行数分摊到本商品行** |
| 17 | `inst_cmdty_income_pay_amt` | 当日支付订单中**即享咖啡品类商品金额**（本商品行口径，最干净）|
| 18 | `cmdty_ord_cnt` | 商品**下单件数**（不限订单状态）|

> 分组合计：3（A）+ 1（B）+ 9（C）+ 5（D）= **18 字段**。

---

## 四、使用注意点（六条）

### ① 引擎是 Doris，不是 Hive

```sql
-- ❌ Hive 引擎下会报 Table or view not found
select 1 from dw_drs_ads.ads_inst_mem_cmdty_behavior_d_1d_uniq limit 0
-- ✅ 切到 Doris 引擎
```

同族 `dept` 版同样是 Doris，`dwm_*` / `dws_*` 才是 Hive。**跨引擎不能 join。**

### ② 没有渠道 / 城市 / 门店字段

本表**不能**独立做「广州+杭州」「私域小程序」「即享售卖门店」这类限定。标准做法：

```sql
with user_pool as (      -- dept 版筛人群池
    select dt, mem_id
    from dw_drs_ads.ads_inst_mem_dept_behavior_d_1d_uniq
    where dt between '...' and '...'
      and city_name in ('广州','杭州')
      and first_channel_name = '私域'
      and third_channel_name = 'app/微信小程序'
      and is_inst_sale_shop = 1
    group by dt, mem_id
),
beh as (                 -- 本表取商品级行为
    select dt, mem_id, max(is_mem_menu_cmdty_bw) as bw ...
    from dw_drs_ads.ads_inst_mem_cmdty_behavior_d_1d_uniq
    where dt between '...' and '...' and cmdty_code = 'SP4386'
    group by dt, mem_id
)
select ...
from beh b left join user_pool u on b.dt = u.dt and b.mem_id = u.mem_id
where 1 = 1
-- 曝光/点击：不加 u 的条件（只有私域资源位产生曝光，加了会清空）
-- 下单/金额：加 u.mem_id is not null
```

### ③ `is_inst_ord_mem` 含未支付，金额是支付口径

`is_inst_ord_mem` = 下单（不限状态）；`inst_cmdty_income_pay_amt` = **支付**金额。两者口径不一致，同一行里混用会得到「下单人数 > 金额对应人数」的矛盾。

**要口径自洽**：下单人数配 `is_inst_ord_mem`，支付人数配 `is_inst_ord_pay_mem` + 支付金额。

### ④ 一人一天一商品可能多行？先验

字段名带 `uniq` 说明已去重，但**建议首次使用时验一次**：

```sql
select count(*) as 行数, count(distinct concat(dt,'|',mem_id,'|',cmdty_code)) as 唯一键数
from dw_drs_ads.ads_inst_mem_cmdty_behavior_d_1d_uniq
where dt = '2026-11-17'
```

行数 = 唯一键数 → 真正的 uniq；否则需先 `group by` 压平再用 `max()` / `sum()`。

### ⑤ 严格漏斗要累积条件

```sql
-- ❌ 各级独立统计，会出现「下单人 > 点击人」
count(distinct if(is_inst_ord_pay_mem = 1, mem_id, null))
-- ✅ 累积
count(distinct if(is_mem_menu_cmdty_bw = 1 and is_mem_menu_cmdty_ck = 1
                  and is_mem_menu_cmdty_cmdty_ck = 1 and is_inst_productdetail_bw = 1
                  and is_inst_ord_pay_mem = 1, mem_id, null))
```

### ⑥ 严格漏斗按天会断链

全链路要求**同一天**完成。实际场景常是今天曝光、明天点、后天买，跨天就断。所以：

- **按天严格漏斗** —— 人数会很小，看趋势可以，看转化率会严重低估
- **周期严格漏斗** —— 整段时间内累积（按 `mem_id` 聚合而非 `dt + mem_id`），这才是真实转化率

报数时必须说清用的是哪个。

---

## 五、类型说明（待补）

本次拿到的 DDL 是**注释清单**（字段名 + 中文语义），**没有字段类型**。`field_status` 标为 🟡。

需要用 `SHOW CREATE TABLE dw_drs_ads.ads_inst_mem_cmdty_behavior_d_1d_uniq`（Doris 引擎下）核定后补全：

- `is_*` 系列：大概率 `tinyint` / `int`
- 两个金额字段：大概率 `decimal(18,2)`，但**不确定**
- `cmdty_ord_cnt`：大概率 `int` / `bigint`
- `dt` / `cmdty_code` / `cmdty_name` / `mem_id`：大概率 `varchar` / `bigint`，**未知**

> ⚠️ 在类型核定前，金额字段不要直接做 `sum` 外的运算（如除法），先 `cast` 成 `decimal`。

---

> 关联：[[数据字典索引]] · [[SQL经验库]] · [[门店即享复购分析SQL模板]] · [[门店即享渠道价值评估-SP4386]] · [[fact_dwd_log_c_menu_cmdty_detail_d_inc]]
