---
created: 2026-08-26
updated: 2026-08-26
tags: [企业, 数据, 字典, 埋点日志]
field_status: ⚠️ 部分（由AB实验分析SQL提炼，待补全完整schema）
source: 用户提供 @ 2026-08-26
---

# dwm_mg_log_abtest_user_d_1d — AB实验真实命中用户日表

**数据库**：`dw_dwm`

## 表说明

- **层级**：DWM（明细中间层）
- **用途**：记录**当天真实上报命中**目标 AB 实验的用户（天 × 人 × 实验 × 实验组 × 平台 粒度）
- **⚠️ 与 ADS 预分配表的区别**：本表 = 真实命中口径（用户当天真实上报过实验命中）；ADS 全量预分配表 = 分配了但未必真实命中。**实验人群分析以本表为准，不用 ADS 预分配表**
- **注意**：DWM 可能按会话产生多行，分析时先收敛到 天 × 人 × 实验组 × 平台

## 已知字段（由 AB 实验分析 SQL 提炼，非完整 schema）

| 字段 | 说明 |
|:--|:--|
| `dt` | 分区/日期 |
| `mem_id` | 会员 ID（分析时 CAST 成 STRING 与埋点表 `user_id` 对齐） |
| `test_id` | 实验 ID |
| `test_template_no` | 实验编号（如 `TM119984592869390337`） |
| `test_template_name` | 实验名称 |
| `test_scene` | 实验场景编码 |
| `testgroup_id` | 实验组 ID |
| `test_group_name` | 实验组名称 |
| `platform` | 平台（1/2/3/5，与埋点表一致） |
| `first_report_time` | 首次上报时间 |
| `last_report_time` | 最近上报时间 |

## 典型 SQL

完整 AB 实验分析模板见：[[技能库/AB实验分析SQL模板]]

```sql
-- 真实命中UV：天 × 实验 × 实验组 去重人数
select dt, test_id, test_template_no, testgroup_id,
       count(distinct mem_id) as hit_uv
from dw_dwm.dwm_mg_log_abtest_user_d_1d
where dt between '${start_date}' and '${end_date}'
  and test_template_no = 'TM119984592869390337'
  and platform in (1,2,3,5)
group by 1,2,3,4
```

## 关联表

| 关联表 | 说明 |
|:--|:--|
| [[fact_dwd_log_c_start_retention_detail_d_inc]] | 公共埋点（启动/页面） |
| [[fact_dwd_log_c_luckinpop_detail_d_inc]] | 电商埋点（商详/弹窗） |
| `dim_con_test_template_d_his` | 实验模板维度（字典待补全） |

关联：[[数据字典索引]] · [[技能库/AB实验分析SQL模板]]
