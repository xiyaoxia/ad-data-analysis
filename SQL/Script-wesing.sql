-- wesing
select 
	red.`统计日期`,
	red.dau,
	yellow.`广告收入$` ,
	green.`银币激励广告收入` ,
	yellow.`广告曝光次数` ,
	yellow.ecpm ,
	blue.ecpm ,
	purple.inn + purple.rew as `激励&插屏广告曝光`,
	red.`任务中心渗透` ,
	ifnull(red.`看广告人数` / nullif(red.dau,0),0) as `广告曝光渗透`,
	green.`实际ROI(含分成)` ,
	red.`看广告人数` ,
	purple.inn ,
	purple.rew 
from `核心指标监控` red
left join roi green on green.`日期` = red.`统计日期` 
left join (
	select `数据日期` , ecpm
	from `分场景_广告ecpm_max_topon`
	where `广告类型` = '激励广告'
) blue on blue.`数据日期` = red.`统计日期`
left join `新标签页` yellow on yellow.`数据日期` = red.`统计日期`
left join (
	select 
		mt.`数据日期` ,
		SUM(case when mt.`广告类型` = 'INTER' then mt.`广告曝光次数` else 0 end ) as `inn` ,
		SUM(case when mt.`广告类型` = '激励广告' then mt.`广告曝光次数` else 0 end ) as `rew`
	from `分场景_广告展示_max_topon` mt
	GROUP BY mt.`数据日期`
) purple on purple.`数据日期` = red.`统计日期`
-- !!!!!!!!!!!更改日期
where red.`统计日期`>= 20251228
  and red.`统计日期` <= 20260124
order by red.`统计日期`

