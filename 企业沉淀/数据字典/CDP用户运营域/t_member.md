---
created: 2026-11-19
updated: 2026-11-19
tags: [企业, 数据字典, CDP用户运营域, 会员, 主数据]
field_status: 🔴 部分（仅确认 2 个字段，其余待 DDL）
source: 用户参考 SQL @ 2026-11-19（`lucky_member.t_member`）
---

# lucky_member.t_member — 咖啡侧会员主表

> **全域会员主键映射表**。`id` 就是业务上通称的 **`mem_id`**；`member_no` 是与外部渠道（公域淘宝/抖音/京东）对接的中转编号。
> 库：`lucky_member` · **字段数：待核定**（本篇只记录了实测用到的 2 个关键字段）

---

## 一、表定位

| 项 | 说明 |
|:--|:--|
| 全名 | `lucky_member.t_member` |
| 库 | `lucky_member`（会员中心库） |
| 业务域 | **CDP用户运营域**（会员主数据；如需单独「会员域」可再议） |
| 角色 | **会员主键的唯一权威来源**：`id` = `mem_id`，贯穿门店订单、电商订单、埋点、行为宽表 |
| 关键性 | 🔴 **跨渠道分析的必经节点** —— 门店/自营用 `mem_id`，公域用 `member_no`，两者靠本表打通 |

---

## 二、已确认字段

| # | 字段名 | 语义 | 用途 |
|:-:|:------|:-----|:-----|
| 1 | `id` | **会员主键 = `mem_id`** | 所有门店/电商/行为表里出现的 `mem_id`，来源都是这一列 |
| 2 | `member_no` | **咖啡侧会员编号** | 与 `t_third_member.member_no` 对接，是公域数据的唯一入口键 |

> ⚠️ **类型未核定**：参考 SQL 里用的是 `cast(m.id as string) = cast(sb.mem_id as string)`，说明两侧类型可能不一致（一边数值一边字符串），**做 join 时一律显式 `cast`**。

---

## 三、跨渠道打通链路（本表的核心价值）

```
【门店 / 自营】mem_id  ←── 直接等于 t_member.id
                              │
                              │  t_member.member_no
                              ▼
                    t_third_member.member_no
                              │
                    t_third_member.id
                              │
              t_huibo_member_platform.third_member_id
                              │
              t_huibo_member_platform.platform_member_id
                              │
                  t_third_parent_order.platform_member_id
                              │
                              ▼
                    【公域】淘宝 / 抖音 / 京东订单
```

**反向写 SQL 时的顺序**：

```sql
-- 从 mem_id 出发找公域订单
select ...
from (业务表) b
join lucky_member.t_member m
  on cast(m.id as string) = cast(b.mem_id as string)
join lucky_ethirdparty.t_third_member tm
  on m.member_no = tm.member_no
join lucky_ethirdparty.t_huibo_member_platform hmp
  on tm.id = hmp.third_member_id
join lucky_ethirdparty.t_third_parent_order tpo
  on hmp.platform_member_id = tpo.platform_member_id
 and hmp.platform = tpo.platform          -- 🔴 必须两边都限平台
where ...
```

---

## 四、使用注意点（五条）

### ① `id` 就是 `mem_id`，不需要再找映射

这是最容易绕弯路的地方 —— 很多分析里会出现「`mem_id` 要不要再转一层」的疑问。**不需要**，`t_member.id` 即业务口径的会员 ID。

### ② `member_no` 必须过滤空值

```sql
where m.member_no is not null
  and m.member_no <> ''
```

`member_no` 为空的会员没有绑定任何外部渠道，join `t_third_member` 会产生脏匹配。

### ③ join 一律显式 `cast`

用户参考 SQL 用的是 `cast(m.id as string) = cast(b.mem_id as string)`。不同表的 `mem_id` / `id` 类型可能不同（`bigint` vs `varchar`），隐式转换在 Hive/Doris 上行为不一致。

### ④ 一人在公域可绑多平台

一个 `mem_id` 可能同时有 `TAOBAO` / `DOUYIN` / `JINGDONG` 三个平台账号（`t_huibo_member_platform` 一对多）。**统计人数时要 `count(distinct mem_id)`，不要数绑定关系数。**

🔴 **实测踩过的坑**：曾经用 `distinct mem_id, platform, platform_member_id` 建绑定池，再 join 订单表，同一人多平台账号导致订单**重复匹配、金额放大近一倍**（6,345.24 元 vs 真实 3,495.41 元）。正确做法是**按 `mem_id` 聚合后再关联**。

### ⑤ 公域平台枚举只到三个

`t_huibo_member_platform.platform` 与 `t_third_parent_order.platform` 的枚举均为 `TAOBAO` / `DOUYIN` / `JINGDONG`。**没有拼多多**——业务上公域含拼多多，但数仓未接入。

---

## 五、典型 SQL

```sql
-- 单日活跃会员数与公域绑定率
select count(distinct b.mem_id)                                                     as 门店会员数
     , count(distinct if(hmp.platform_member_id is not null, b.mem_id, null))        as 有公域绑定会员数
     , round(count(distinct if(hmp.platform_member_id is not null, b.mem_id, null)) * 100.0
             / nullif(count(distinct b.mem_id), 0), 2)                               as 公域绑定率
from (select distinct mem_id from dw_dwm.dwm_mg_order_cmdty_market_wide_d_view
      where dt = '2026-11-17' and city_name = '广州' and mem_id is not null) b
join lucky_member.t_member m
  on cast(m.id as string) = cast(b.mem_id as string)
left join lucky_ethirdparty.t_third_member tm
       on m.member_no = tm.member_no
left join lucky_ethirdparty.t_huibo_member_platform hmp
       on tm.id = hmp.third_member_id
      and hmp.is_bind = 1
where 1 = 1
```

**实测参考值**：门店买即享咖啡液的 7,017 人中，**1,158 人（16.5%）** 有公域账号绑定。

---

## 六、待补

| # | 待补 | 怎么补 |
|:-:|:--|:--|
| 1 | **完整 DDL**（字段全集 + 类型 + 注释）| Doris/Hive 引擎下 `select * from lucky_member.t_member limit 0` 或从元数据平台取 `SHOW CREATE TABLE` |
| 2 | **域归属确认** | 当前放在 CDP用户运营域；若团队认为应单列「会员域」，需同步调整索引 |
| 3 | **是否有 `mobile` / 手机号字段** | 若有，可作为 public 与自营的备用关联键 |
| 4 | **会员生命周期字段**（注册时间、等级、状态）| 影响「新客」口径的严谨性 |

---

> 关联：[[数据字典索引]] · [[t_third_member]] · [[t_huibo_member_platform]] · [[t_third_parent_order]] · [[门店即享渠道价值评估-SP4386]] · [[门店即享-SP4386-数据台账]]
