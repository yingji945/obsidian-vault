---
created: 2026-10-12
updated: 2026-10-12
tags: [企业, 数据字典, 订单交易域, 门店订单, DWM, 渠道归因]
field_status: ✅ 完整（4 字段含类型，来源 SHOW CREATE TABLE）
source: 用户提供 CREATE TABLE（2026-10-12）；DDL 时间戳指向建表于 2026-04-17
---

# dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc

> **订单商品归属渠道桥接表** —— 把订单商品挂到「四级渠道 + 三方渠道场域」
> 粒度：1 行 = 1 个订单商品（`order_cmdty_id`）· 分区：`dt`（**string**）· 字段数：**4**

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc` |
| 业务域 | **订单交易域**（门店业务） |
| 角色 | **桥接表**：订单商品 ↔ 渠道归因，服务下游宽表 |
| 粒度 | 订单商品行（`order_cmdty_id`） |
| 层级 | `DWM`（日增量 `_inc`） |
| 分区键 | `dt`（string，日期分区） |
| 字段数 | 4 |
| 存储 | ORC + ZLIB |
| 建表时间 | 2026-04-17（DDL `transient_lastDdlTime` 换算） |

---

## 二、表结构（4 字段）

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `order_cmdty_id` | bigint | 订单商品id |
| 2 | `fourth_channel_id` | bigint | 四级渠道id |
| 3 | `third_site_channel_id` | bigint | 三方渠道场域ID |
| 4 | `third_site_channel_name` | string | 三方渠道场域名称 |

**分区**

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `dt` | string | 日期分区 |

---

## 三、它在血缘里的位置 ⭐

本表是 [[dwm_mg_order_cmdty_market_wide_d_view]]（订单商品渠道归因视图）的**上游 `cb`**：

```
dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc         主表：订单商品基础字段
        │  join on dt + order_cmdty_id
        ▼
dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc      本表：渠道桥（fourth_channel_id / third_site_*）
        │  join on fourth_channel_id
        ▼
dw_dim.dim_channel_level_d_his                      渠道层级维：一~三级渠道 id/name
```

---

## 四、使用注意点

| # | 注意点 |
|:-:|:--|
| 1 | **本表没有渠道名称**（只有 `fourth_channel_id`）：四级渠道名要 join `dw_dim.dim_channel_level_d_his`（下游视图就是这么取的）；本表自带的名称只有 `third_site_channel_name` |
| 2 | **关联键是 `dt + order_cmdty_id`，不是 `order_id`** —— 粒度是订单商品行，一单多商品会有多行 |
| 3 | **`dt` 是 string 类型**（非 date）：join 时两侧都保持字符串，不要隐式转 date，否则分区裁剪可能失效 |
| 4 | 增量表（`_inc`）：每天只写当天分区，跨天分析要按 `dt` 范围扫多分区 |
| 5 | ⚠️ **待验证**：本表是否「只覆盖有渠道归因的订单商品」（即普通无渠道订单可能没有对应行）。若如此，下游视图用的是 `left join`，取数时渠道字段会为 null，**不要用 inner join 统计总量**。建议用一天的 `count(order_cmdty_id)` 与主表对比确认 |

---

## 五、典型 SQL

```sql
-- ① 某天各四级渠道的订单商品数（本表独立使用）
select fourth_channel_id,
       count(distinct order_cmdty_id) as cmdty_cnt
from dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc
where dt = date_sub(current_date(), 1)
group by 1
order by cmdty_cnt desc

-- ② 拿到渠道名称（还原下游视图的 join 写法）
select cb.fourth_channel_id,
       cl.fourth_channel_name,
       cb.third_site_channel_name,
       count(distinct cb.order_cmdty_id) as cmdty_cnt
from dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc cb
left join dw_dim.dim_channel_level_d_his cl
       on cb.fourth_channel_id = cl.fourth_channel_id
      and cl.dt = date_sub(current_date(), 1)
where cb.dt = date_sub(current_date(), 1)
group by 1,2,3
order by cmdty_cnt desc

-- ③ 筛三方渠道场域（如抖音）
select third_site_channel_id, third_site_channel_name,
       count(distinct order_cmdty_id) as cmdty_cnt
from dw_dwm.dwm_mg_order_cmdty_channel_bridge_d_inc
where dt = date_sub(current_date(), 1)
group by 1,2
order by cmdty_cnt desc
```

---

## 六、关联

- 索引：[[数据字典索引]] · 分层：[[数据仓库分层说明]]
- **下游（本表喂它）**：[[dwm_mg_order_cmdty_market_wide_d_view]] —— 订单商品渠道归因视图（别名 `cb`）
- **上游/维表**：`dw_dim.dim_channel_level_d_his` —— 渠道层级维（一~四级渠道），**尚未建字典**
- 同域兄弟：[[dwm_mg_order_cmdty_market_wide_d_view]]（视图）

---

## 七、待补

| 对象 | 说明 |
|:--|:--|
| `dw_dim.dim_channel_level_d_his` | 渠道层级维（提供一/二/三级渠道 id+name、四级渠道 name），**未建字典** |
| `dw_dwm.dwm_mg_order_cmdty_market_wide_d_inc` | 订单商品营销宽表主表（视图的 `oc`），**未建字典**（含 `order_status` 枚举、`cmdty_settle_income_amt` 口径） |
| `dw_dim.dim_sku_ord_rmk_d_a` | SKU 备注维（杯型/温度），**未建字典** |
