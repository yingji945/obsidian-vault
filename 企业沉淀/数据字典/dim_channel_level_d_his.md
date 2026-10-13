---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 门店业务域, 维度表, 渠道归因, dw_dim]
field_status: ✅ 完整（13 字段含类型，来源 SHOW CREATE TABLE）
source: 用户提供 CREATE TABLE（2026-10-12）；DDL 时间戳指向建表于 2025-10-15
---

# dw_dim.dim_channel_level_d_his

> **渠道归因维表** —— 提供一~四级渠道的 id / 名称 / 简称（门店订单与三方场域的渠道归属标准字典）
> 粒度：1 行 = 1 个**四级渠道**（含其上级三级/二级/一级渠道）· 分区：`dt`（**快照日期**）· 字段数：**13**

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_dim.dim_channel_level_d_his` |
| 库 | `dw_dim`（**维表层**，不是 `dw_dwm`） |
| 业务域 | **门店业务域**（渠道归因维表，服务门店订单的渠道归属） |
| 角色 | **渠道归因字典**：把渠道 id 翻译成名称，做一~四级渠道维度分析 |
| 粒度 | 四级渠道（1 行 = 1 个 `fourth_channel_id`） |
| 表类型 | **`_his` 历史快照表**（⚠️ 见第五节陷阱 1） |
| 分区键 | `dt`（string，**快照日期**，非业务日期） |
| 字段数 | 13（第四节） |
| 存储 | ORC + ZLIB |
| 最近变更 | 2025-10-15（DDL 时间戳） |

---

## 二、它在血缘里的位置 ⭐

```
dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc   渠道桥（订单商品 → 四级渠道 id + 三方场域）
        │  fourth_channel_id
        ▼
dw_dim.dim_channel_level_d_his                   ← 本表（渠道归因维）
        │
        ├──► dw_dwm.dwm_mg_order_cmdty_market_wide_d_view   订单商品渠道归因视图
        │         （取 first/second/third_channel_* + fourth_channel_name 共 7 个字段）
        ▼
    一 / 二 / 三 / 四级渠道名称与简称
```

---

## 三、渠道层级语义（重要）

| 层级 | id 类型 | 可用名称 | 说明 |
|:--|:--|:--|:--|
| **一级**（最大） | `int` ⚠️ | `first_channel_name` | **无简称** |
| **二级** | `int` ⚠️ | `second_channel_name`、`second_channel_short_name` | |
| **三级** | `bigint` | `third_channel_name`、`third_channel_short_name`、`third_channel_total_name`（汇总名）、`third_channel_dept_name`（运营名） | **名称变体最多**：报表口径需确认用哪个 |
| **四级**（最细） | `bigint` | `fourth_channel_name`、`fourth_channel_short_name` | 与渠道桥 join 的键 |

> ⚠️ **类型不统一**：一级/二级的 id 是 `int`，三级/四级的 id 是 `bigint`。
> 与 bigint 字段比较时会触发隐式类型转换，**大表上可能影响谓词下推**，需要时显式 `cast(x as bigint)`。

---

## 四、字段清单（13 字段）

### A. 四级渠道（3 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `fourth_channel_id` | `bigint` | 四级渠道id（**与渠道桥 join 的键**） |
| 2 | `fourth_channel_name` | `string` | 四级渠道名称 |
| 3 | `fourth_channel_short_name` | `string` | 四级渠道简称 |

### B. 三级渠道（5 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 4 | `third_channel_id` | `bigint` | 三级渠道id |
| 5 | `third_channel_name` | `string` | 三级渠道名称 |
| 6 | `third_channel_short_name` | `string` | 三级渠道简称 |
| 7 | `third_channel_total_name` | `string` | 三级渠道汇总名称 |
| 8 | `third_channel_dept_name` | `string` | 三级渠道运营名称 |

### C. 二级渠道（3 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 9 | `second_channel_id` | `int` ⚠️ | 二级渠道id |
| 10 | `second_channel_name` | `string` | 二级渠道名称 |
| 11 | `second_channel_short_name` | `string` | 二级渠道简称 |

### D. 一级渠道（2 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 12 | `first_channel_id` | `int` ⚠️ | 一级渠道id |
| 13 | `first_channel_name` | `string` | 一级渠道名称（**无简称**） |

### 分区字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `dt` | `string` | **快照日期**（不是业务发生日期） |

---

## 五、口径与使用注意点

| # | 注意点 |
|:-:|:--|
| 1 | 🔴 **最大的坑 —— 这是快照表，但下游视图不按业务日期取快照。** 门店业务域的下游视图 [[dwm_mg_order_cmdty_market_wide_d_view]] 用的是 `date_sub(current_date(),1)`（**永远取"昨天"的快照**），**不跟随订单自己的 `dt`**。后果：①渠道发生改名/归属调整后，**回看历史订单会看到"现在的"渠道归属**，历史口径会漂移；②任何"某天渠道名"的口径都等于"今天最新的渠道字典"，不是那天的字典。**要做严格历史归因，必须自己按 `订单 dt` 关联本表的 `dt` 分区**（`cl.dt = oc.dt`）。 |
| 2 | **快照表的数据量**：`_his` 每天一份全量快照，取最新用 `dt = date_sub(current_date(),1)`，不要 `dt = max(dt)`（后者全表扫描）。 |
| 3 | **粒度是四级渠道**：要一/二/三级汇总直接在本表聚合（一~三级字段已冗余在同一行），**不需要 join 上级表**。 |
| 4 | **名称变体易错**：三级渠道有 4 个名称字段（`name` / `short_name` / `total_name` / `dept_name`），做报表前**先确认业务口径用哪个**（展示一般用 `short_name`，运营口径常为 `dept_name`）。一级渠道**没有**简称。 |
| 5 | **只有渠道 id/name，没有渠道属性**（如渠道类型、是否线上）——需要那些属性要另找渠道主数据表。 |
| 6 | 本表**不含订单/商品信息**，纯字典；它不随订单变化，只随渠道组织结构变化。 |

---

## 六、典型 SQL

```sql
-- ① 看最新快照的全部渠道层级（一~四级）
select first_channel_id, first_channel_name,
       second_channel_id, second_channel_name,
       third_channel_id, third_channel_name, third_channel_dept_name,
       fourth_channel_id, fourth_channel_name, fourth_channel_short_name
from dw_dim.dim_channel_level_d_his
where dt = date_sub(current_date(), 1)

-- ② 给订单商品挂渠道名（= 下游视图的写法，快照取"昨天"）
select cb.fourth_channel_id,
       cl.first_channel_name, cl.second_channel_name, cl.third_channel_name, cl.fourth_channel_name,
       count(distinct oc.order_id) as order_cnt
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc oc
join dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc cb
  on oc.dt = cb.dt and oc.order_cmdty_id = cb.order_cmdty_id
left join dw_dim.dim_channel_level_d_his cl
  on cl.dt = date_sub(current_date(), 1)      -- ⚠️ 视图口径：固定取昨天
 and cb.fourth_channel_id = cl.fourth_channel_id
where oc.dt = date_sub(current_date(), 1)
group by 1,2,3,4,5

-- ③ 严格历史归因（快照跟着订单日期走 —— 与视图口径不同，注意对比）
select oc.dt, cl.first_channel_name,
       count(distinct oc.order_id) as order_cnt
from dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc oc
join dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc cb
  on oc.dt = cb.dt and oc.order_cmdty_id = cb.order_cmdty_id
left join dw_dim.dim_channel_level_d_his cl
  on cl.dt = oc.dt                              -- ✅ 用订单当天的字典
 and cb.fourth_channel_id = cl.fourth_channel_id
where oc.dt between date_sub(current_date(), 7) and date_sub(current_date(), 1)
group by 1,2
```

---

## 七、关联

- 索引：[[数据字典索引]] · 分层：[[数据仓库分层说明]]
- **下游使用方**：[[dwm_mg_order_cmdty_market_wide_d_view]] —— 订单商品渠道归因视图（取本表 7 个字段）
- **间接上游**：[[dwm_mg_order_cmdty_channel_bridge_d_inc]] —— 渠道桥（`fourth_channel_id` 由此而来）

> 📌 **域内维表**：本表服务于**门店业务**。虽建在 `dw_dim` 库（维表层），但用途单一，故与门店业务域的表同列于索引。

---

## 八、待补

| 对象 | 说明 |
|:--|:--|
| 渠道字典**业务含义** | ⚠️ 哪些渠道对应哪些实际三方（抖音/美团/饿了么等）——DDL 只给 id/name，**具体映射需看数据或找运营** |
| 三级渠道 4 个名称的**口径约定** | `name` / `short_name` / `total_name` / `dept_name` 分别用于什么场景，**待与业务确认** |
| [[dim_sku_ord_rmk_d_a]] | 订单商品属性维（杯型/温度 等 44 属性） | ✅ **已建字典**（2026-10-12） |
