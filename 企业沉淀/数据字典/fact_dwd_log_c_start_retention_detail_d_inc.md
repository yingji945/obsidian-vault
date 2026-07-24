---
created: 2026-07-24
tags: [企业, 数据, 字典, 电商DWD]
field_status: 待补充
---

# fact_dwd_log_c_start_retention_detail_d_inc — 启动/页面浏览明细

**数据库**：`dw_dwd`

> ⚠️ **字段待补充**

## 已知字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `event_code` | varchar | 事件编码 |
| `prop_query_source` | string | 渠道码 |
| `prop_page_id` | string | 页面 ID |
| `platform` | tinyint | 平台 |

## 使用注意点

- **渠道码过滤**：非投放渠道 = `prop_query_source IS NULL OR prop_query_source NOT IN (投放渠道列表)`
- **投放渠道列表**：见 [[数据字典索引]] 中的投放渠道码

关联：[[数据字典索引]]
