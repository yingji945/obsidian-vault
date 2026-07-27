---
created: 2026-07-25
tags: [企业, 数据, 字典, CDP, ADS]
field_status: ✅ 完整
source: 用户提供 @ 2026-07-25
---

# dw_ads_lucky_cdp.t_offline_user_group_data — CDP 离线用户分群数据

**数据库**：`dw_ads_lucky_cdp`

**层级**：`ADS`（应用数据层）

## 表结构

| # | 字段名 | 类型 | 说明 |
|:-:|:------|:----|:-----|
| 1 | `mem_id` | bigint | 用户 ID（关联 `t_member.id`） |

## 使用注意点

- **分群成员表**：这张表是一个**用户分群的成员列表**，当前分群下的所有用户 ID 都在这里
- **单字段查询效率极高**：只有 `mem_id`，`SELECT DISTINCT mem_id` 或 join 操作非常快
- **无分区字段**：每次分群会覆盖全量数据（非增量），查询时不需要 `dt` 过滤
- **使用场景**：
  - 圈定某个用户分群后，用这张表 join 其他事实表做定向分析
  - 例如：分群 + `dws_eorder_eorder_d_his_combine` → 分析分群用户的客单价
  - 分群 + `t_wecom_external_user_history` → 分析分群用户在企微的触达情况

## 典型 SQL

```sql
-- 分析某个用户分群的电商消费情况
select
  count(distinct o.mem_id) as user_cnt,
  count(distinct o.eorder_id) as order_cnt,
  sum(o.eorder_income) as total_income
from dw_ads_lucky_cdp.t_offline_user_group_data g
inner join dw_dws.dws_eorder_eorder_d_his_combine o
  on g.mem_id = o.mem_id
where o.dt = date_sub(current_date(), 1)
  and o.eorder_status in ('2','3','7','8','9')
  and o.total_ecmdty_payable_money <> 0;
```

关联：[[数据字典索引]] · [[数据仓库分层说明]] · [[dws_eorder_eorder_d_his_combine]]
