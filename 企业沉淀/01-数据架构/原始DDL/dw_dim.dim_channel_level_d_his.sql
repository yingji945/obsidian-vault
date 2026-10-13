CREATE TABLE
`dim_channel_level_d_his` (
`fourth_channel_id` bigint COMMENT '四级渠道id',
`fourth_channel_name` string COMMENT '四级渠道名称',
`fourth_channel_short_name` string COMMENT '四级渠道简称',
`third_channel_id` bigint COMMENT '三级渠道id',
`third_channel_name` string COMMENT '三级渠道名称',
`third_channel_short_name` string COMMENT '三级渠道简称',
`third_channel_total_name` string COMMENT '三级渠道汇总名称',
`third_channel_dept_name` string COMMENT '三级渠道运营名称',
`second_channel_id` int COMMENT '二级渠道id',
`second_channel_name` string COMMENT '二级渠道名称',
`second_channel_short_name` string COMMENT '二级渠道简称',
`first_channel_id` int COMMENT '一级渠道id',
`first_channel_name` string COMMENT '一级渠道名称'
) COMMENT '渠道归因维表' PARTITIONED BY (`dt` string COMMENT '日期分区') ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.orc.OrcSerde' STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.orc.OrcInputFormat' OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat' LOCATION 'obs://lts-bigdata-hive-obs-prod/user/hive/warehouse/dw_dim.db/dim_channel_level_d_his' TBLPROPERTIES (
'bucketing_version' = '2',
'orc.compress' = 'ZLIB',
'transient_lastDdlTime' = '1760519500'
)
