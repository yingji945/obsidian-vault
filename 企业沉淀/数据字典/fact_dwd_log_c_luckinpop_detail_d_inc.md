---
created: 2026-07-24
tags: [企业, 数据, 字典, 电商DWD]
field_status: 待补充
---

# fact_dwd_log_c_luckinpop_detail_d_inc — 电商 DWD 埋点表

**数据库**：`dw_dwd`

> ⚠️ **字段待补充**

## 已知字段

| 字段名 | 类型 | 说明 |
|:------|:----|:-----|
| `event_code` | varchar | 事件编码 |
| `user_id` | bigint | 用户 ID |
| `prop_data` | string | JSON 扩展字段 |
| `prop_url` | string | 页面 URL |
| `platform` | tinyint | 平台：`1`=iOS, `2`=安卓, `3`=小程序, `5`=支付宝, `6`=抖音 |

## 使用注意点

- **mall 入口识别**：`event_code = 'web_page_start'` + `prop_data.web_url LIKE 'https://m.lkcoffee.com/pmall%'`
- **商品详情页**：`event_code = 'lucinpop_productdetail_start'`
- **`prop_data` 是 JSON 字符串**，解析效率较低，避免不必要的 JSON 解析

关联：[[数据字典索引]]
