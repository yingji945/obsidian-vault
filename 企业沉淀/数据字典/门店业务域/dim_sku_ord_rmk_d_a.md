---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 门店业务域, 维度表, 商品属性, 客制化, dw_dim]
field_status: ✅ 完整（44 字段含类型，来源 SHOW CREATE TABLE）
source: 用户提供 CREATE TABLE（2026-10-12）；DDL last_modified 2026-01-05
---

# dw_dim.dim_sku_ord_rmk_d_a

> **订单商品属性维表** —— 按 SKU 提供商品属性备注：杯型、温度、糖度、奶基、风味、加料、咖啡/茶参数，以及**周边商品**（颜色/图案/材质）
> 粒度：1 行 = 1 个 SKU（`sku_code`）· 分区：`dt`（**快照日期**）· 字段数：**44**（**全部 string**）

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_dim.dim_sku_ord_rmk_d_a` |
| 库 | `dw_dim`（维表层） |
| 业务域 | **门店业务域**（商品属性维） |
| 角色 | **商品属性字典**：把 SKU 翻译成"什么杯型/什么温度/加了什么料"，支撑客制化与商品结构分析 |
| 粒度 | SKU（1 行 = 1 个 `sku_code`） |
| 表类型 | 快照表（⚠️ 见第五节陷阱 2） |
| 分区键 | `dt`（string，快照日期） |
| 字段数 | 44（第四节，9 组）· **类型全部为 `string`** |
| 最近变更 | 2026-01-05（DDL 时间戳） |

---

## 二、它在血缘里的位置 ⭐

```
dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc   订单商品基础表
        │  oc.sku_code = sku.sku_code            ← 直接关联，不经过渠道桥
        ▼
dw_dim.dim_sku_ord_rmk_d_a                    ← 本表（商品属性维）
        │
        ▼
dw_dwm.dwm_mg_order_cmdty_market_wide_d_view  订单商品渠道归因视图
              （取 cup_rmk_name / temp_rmk_name 共 2 个字段）
```

> 视图里的实际写法（已核对）：
> ```sql
> left join dw_dim.dim_sku_ord_rmk_d_a sku
>        on oc.sku_code = sku.sku_code
>       and sku.dt = date_sub(current_date(), 1)
> ```

---

## 三、⚠️ 新旧同义字段并存（最容易取错的地方）🔴

本表**同时存在新旧两套**杯型/温度字段：

| 属性 | ✅ 新口径（**下游视图用的**） | ⚠️ 旧口径（仍在表内） |
|:--|:--|:--|
| 杯型 | `cup_rmk_name`（杯型**(新)**） | `cup_size_rmk_name`（杯型） |
| 温度 | `temp_rmk_name`（温度**(新)**） | `tempr_rmk_name`（温度） |

> **做分析必须用带「(新)」的两个字段** —— 门店业务域的视图用的就是它们。
> 旧字段是否已停止更新**未确证**；但既然下游口径已切新，混用会造成同一指标两个数。
> 另有 `concentration_rmk_name`（浓度）与 `coffee_degree_rmk_name`（咖啡浓度）两个浓度字段，**口径差异待与业务确认**。

---

## 四、字段清单（44 字段 · 9 组 · 全部 string）

### A. 标识与关联键（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `sku_code` | `string` | 商品skuCode |
| 2 | `sku_name` | `string` | 商品sku名称 |
| 3 | `cmdty_code` | `string` | 商品code |
| 4 | `cmdty_name` | `string` | 商品名称 |

### B. 杯型与温度 ⭐（新旧口径并存）（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 5 | `cup_rmk_name` | `string` | 杯型(新) |
| 6 | `temp_rmk_name` | `string` | 温度(新) |
| 7 | `cup_size_rmk_name` | `string` | 杯型 |
| 8 | `tempr_rmk_name` | `string` | 温度 |

### C. 糖 / 冰 / 浓度（6 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 9 | `sugar_rmk_name` | `string` | 糖 |
| 10 | `sugar_degree_rmk_name` | `string` | 糖度 |
| 11 | `zero_calorie_rmk_name` | `string` | 0卡糖 |
| 12 | `ice_hot_rmk_name` | `string` | 冰热属性 |
| 13 | `concentration_rmk_name` | `string` | 浓度 |
| 14 | `coffee_degree_rmk_name` | `string` | 咖啡浓度 |

### D. 奶基与奶（7 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 15 | `replace_base_milk_rmk_name` | `string` | 更换基础奶基 |
| 16 | `replace_origin_milk_rmk_name` | `string` | 更换原创奶基 |
| 17 | `add_milk_base_rmk_name` | `string` | 添加奶基 |
| 18 | `milk_base_rmk_name` | `string` | 奶基 |
| 19 | `milk_rmk_name` | `string` | 奶 |
| 20 | `cream_rmk_name` | `string` | 奶油 |
| 21 | `milk_cap_rmk_name` | `string` | 奶盖 |

### E. 咖啡（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 22 | `coffee_bean_rmk_name` | `string` | 咖啡豆 |
| 23 | `coffee_liquid_rmk_name` | `string` | 咖啡液 |
| 24 | `extract_rmk_name` | `string` | 萃取方式 |
| 25 | `roast_rmk_name` | `string` | 烘焙度 |

### F. 茶（2 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 26 | `tea_flavor_rmk_name` | `string` | 茶风味 |
| 27 | `tea_dregs_rmk_name` | `string` | 茶底 |

### G. 风味与加料（8 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 28 | `flavor_rmk_name` | `string` | 风味 |
| 29 | `taste_flavor_rmk_name` | `string` | 口味 |
| 30 | `sauce_rmk_name` | `string` | 酱 |
| 31 | `top_rmk_name` | `string` | 饮品顶部 |
| 32 | `toppings_rmk_name` | `string` | 小料 |
| 33 | `jelly_rmk_name` | `string` | 冻冻 |
| 34 | `bubble_rmk_name` | `string` | 气泡 |
| 35 | `charge_rmk_name` | `string` | 加料 |

### H. 酒精与规格（2 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 36 | `alcohol_rmk_name` | `string` | 酒精 |
| 37 | `spec_rmk_name` | `string` | 规格 |

### I. 周边商品属性（非饮品）（7 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 38 | `colour_rmk_name` | `string` | 颜色 |
| 39 | `color_code_rmk_name` | `string` | 色号 |
| 40 | `design_rmk_name` | `string` | 图案 |
| 41 | `variety_rmk_name` | `string` | 品种 |
| 42 | `function_rmk_name` | `string` | 功能 |
| 43 | `part_rmk_name` | `string` | 成分 |
| 44 | `ingredients_rmk_name` | `string` | 配料 |
### 分区字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `dt` | `string` | 快照日期（不是业务发生日期） |

---

## 五、口径与使用注意点

| # | 注意点 |
|:-:|:--|
| 1 | **属性值是「备注文本」而非编码**：44 个字段全是 `string`，取值形如「大杯」「少糖」这类中文备注。**做分布统计前先 `group by` 看实际取值**，不要假设枚举 |
| 2 | 🔴 **快照表，但下游不按业务日期取快照**：视图用 `sku.dt = date_sub(current_date(),1)`（固定"昨天"），**不跟随订单 `dt`**。若商品属性在事后被修改（改名/改规格），**回看历史订单会拿到"现在的"属性** → 历史口径漂移。严格历史分析要写成 `sku.dt = oc.dt` |
| 3 | **关联键是 `sku_code`**（不是 `cmdty_code`）；本表**直接与订单商品表 join**，不经过渠道桥 |
| 4 | **全品类属性表**：不只饮品——`colour_rmk_name`（颜色）/`design_rmk_name`（图案）/`part_rmk_name`（成分）等是**周边商品**字段。做饮品分析时注意排除周边 |
| 5 | 命名统一为 `*_rmk_name`（rmk = remark 备注）；4 个非 rmk 字段是标识类（`sku_code`/`sku_name`/`cmdty_code`/`cmdty_name`） |
| 6 | **糖/冰/奶基等是"最终属性"**（如「更换燕麦奶」），不是标准配方——反映的是用户下单时的选择，适合做**客制化率**分析 |

---

## 六、典型 SQL

```sql
-- ① 某天杯型 / 温度分布（新口径 —— 与下游视图一致）
select sku.cup_rmk_name, sku.temp_rmk_name,
       count(distinct oc.order_cmdty_id) as cmdty_cnt,
       sum(oc.cmdty_sale_cnt)            as sale_cnt
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc oc
join dw_dim.dim_sku_ord_rmk_d_a sku
  on oc.sku_code = sku.sku_code
 and sku.dt = date_sub(current_date(), 1)
where oc.dt = date_sub(current_date(), 1)
  and oc.order_cmdty_situation = 1
group by 1,2
order by sale_cnt desc

-- ② 新旧口径是否有差异（若数值不相等，说明旧字段另有口径）
select count(*) as total,
       sum(if(cup_size_rmk_name <> cup_rmk_name, 1, 0))      as cup_diff,
       sum(if(tempr_rmk_name    <> temp_rmk_name, 1, 0))     as temp_diff
from dw_dim.dim_sku_ord_rmk_d_a
where dt = date_sub(current_date(), 1)

-- ③ 客制化率（有加料/换奶基的订单商品占比）
select oc.dt,
       count(distinct oc.order_cmdty_id) as cmdty_cnt,
       count(distinct if(coalesce(sku.charge_rmk_name, sku.toppings_rmk_name) is not null,
                         oc.order_cmdty_id, null)) as customized_cnt,
       round(count(distinct if(coalesce(sku.charge_rmk_name, sku.toppings_rmk_name) is not null,
                               oc.order_cmdty_id, null)) / count(distinct oc.order_cmdty_id), 4) as custom_rate
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc oc
left join dw_dim.dim_sku_ord_rmk_d_a sku
  on oc.sku_code = sku.sku_code
 and sku.dt = date_sub(current_date(), 1)
where oc.dt = date_sub(current_date(), 1)
group by oc.dt
```

---

## 七、关联

- 索引：[[数据字典索引]] · 分层：[[数据仓库分层说明]]
- **下游使用方**：[[dwm_mg_order_cmdty_market_wide_d_view]] —— 订单商品渠道归因视图（取本表 2 个字段 `cup_rmk_name` / `temp_rmk_name`）
- **上游主表**：[[dwm_mg_order_cmdty_market_wide_d_inc]] —— 订单商品基础表（经 `sku_code` 关联本表）
- **同族维表**：[[dim_channel_level_d_his]] —— 渠道归因维（两者都是门店业务域的维表，且**都有快照口径陷阱**）

---

## 八、待补

| 对象 | 说明 |
|:--|:--|
| 旧字段是否废弃 | `cup_size_rmk_name` / `tempr_rmk_name` 是否仍更新，**待与业务确认**（建议先跑第六节 SQL ②） |
| 两个浓度字段口径 | `concentration_rmk_name` vs `coffee_degree_rmk_name`，**含义差异待确认** |
| 属性取值清单 | 44 个字段的实际取值（如杯型有哪些值）——可跑 `group by` 生成，**待补充到本文档** |
