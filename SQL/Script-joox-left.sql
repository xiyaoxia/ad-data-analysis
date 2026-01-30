-- joox左边 切换国家还需要换核心链路的表
set 
	/*国家:HK TH 小计*/
	@country = '小计',
	/*国家：香港 泰国 小计（all）*/
	@country_cn = '小计（all）';
with rev as(
	select `日期`,`国家`,`广告类型`,`广告场景`,`收入￥`,`ecpm￥`,`曝光次数`
	from `广告收入数据` 
	where `国家`= @country and `广告场景`='小计'
-- !!!!!!!!!!!更改日期
	and `日期`>= 20251228 and `日期`<= 20260124
)
select 
	tdau.`日期` ,
	tdau.dau ,
-- 	大盘广告收益￥
	SUM(case when rev.`广告类型`='小计' then rev.`收入￥` else 0 end ) as `大盘广告收益￥`,
-- 	大盘ecpm-￥
	SUM(case when rev.`广告类型`='小计' then rev.`ecpm￥` else 0 end ) as `大盘ecpm-￥`,
-- 	大盘广告曝光总次数
	SUM(case when rev.`广告类型`='小计' then rev.`曝光次数` else 0 end ) as `大盘广告曝光总次数`,
-- 	免模收入
	SUM(case when rev.`广告类型`='免模' then rev.`收入￥` else 0 end ) as `免模收入`,
-- 	免模ecpm
	SUM(case when rev.`广告类型`='免模' then rev.`ecpm￥` else 0 end ) as `免模ecpm`,
-- 	网赚收入
	SUM(case when rev.`广告类型`='网赚' then rev.`收入￥` else 0 end ) as `网赚收入`,
-- 	网赚ecpm
	SUM(case when rev.`广告类型`='网赚' then rev.`ecpm￥` else 0 end ) as `网赚ecpm`,
	tdau.`任务中心渗透`,
	MAX(impress.`人均看广告次数`) as `人均看广告次数` ,
-- 	网赚广告曝光次数
	SUM(case when rev.`广告类型`='网赚' then rev.`曝光次数` else 0 end ) as `网赚广告曝光次数`,
-- 	网赚广告渗透
	IFNULL( round(MAX(impress.`广告曝光人数`) / nullif(tdau.dau, 0),9),0) AS `网赚广告渗透`,
-- 	原生收入
	SUM(case when rev.`广告类型`='原生' then rev.`收入￥` else 0 end ) as `原生收入`,
-- 	原生ecpm
	SUM(case when rev.`广告类型`='原生' then rev.`ecpm￥` else 0 end ) as `原生ecpm`,
-- 	原生广告曝光次数
	SUM(case when rev.`广告类型`='原生' then rev.`曝光次数` else 0 end ) as `原生广告曝光次数`,
	MAX(IFNULL(impress.`广告曝光人数`, 0)) as `网赚广告曝光人数`
from rev
/*dau总表 切换国家还需要换核心链路的表*/
-- !!!!!!!!!!!这里需要切换表
left join  `核心任务链路all` tdau on tdau.`日期`  = rev.`日期`
left join (
	select `日期`, `人均看广告次数`, `广告曝光人数`
	from `广告链路`
	where `广告链路`.`国家` = @country_cn
)impress on impress.`日期` = rev.`日期`
group by tdau.`日期`,tdau.dau,tdau.`任务中心渗透`
order by tdau.`日期` 

