-- joox右边
set 
	/*国家:HK TH 小计*/
	@country = 'HK' ;
with reva as(
	select 
	rev.`日期` ,
	MAX(case when rev.`广告类型`='免模' and rev.`广告场景`='reward' then rev.`曝光次数` else 0 end) as `免模激励广告曝光次数`,
	MAX(case when rev.`广告类型`='免模' and rev.`广告场景`='inter' then rev.`曝光次数`else 0 end) as `免模插屏广告曝光次数`,
	MAX(case when rev.`广告类型`='网赚' and rev.`广告场景`='reward' then rev.`曝光次数`else 0 end) as `网赚激励广告曝光次数`,
	MAX(case when rev.`广告类型`='网赚' and rev.`广告场景`='inter' then rev.`曝光次数`else 0 end) as `网赚插屏广告曝光次数`,
	MAX(case when rev.`广告类型`='小计' and rev.`广告场景`='reward' then rev.`曝光次数`else 0 end) as `大盘激励广告曝光次数`,
	MAX(case when rev.`广告类型`='小计' and rev.`广告场景`='inter' then rev.`曝光次数`else 0 end) as `大盘插屏广告曝光次数`
	from `广告收入数据` rev
-- !!!!!!!!!!!更改日期
	where rev.`日期` >= 20251228 and rev.`日期` <= 20260124 and rev.`国家` = @country
	group by rev.`日期`
)
select 
	`日期`,
	`免模激励广告曝光次数`,
	`免模插屏广告曝光次数`,
	`网赚激励广告曝光次数`,
	`网赚插屏广告曝光次数`,
	`大盘激励广告曝光次数`,
	`大盘插屏广告曝光次数`,
	`免模激励广告曝光次数`+`免模插屏广告曝光次数` as `免模激励&插屏广告曝光次数`,
	`网赚激励广告曝光次数`+`网赚插屏广告曝光次数` as `网赚激励&插屏广告曝光次数`,
	`大盘激励广告曝光次数`+`大盘插屏广告曝光次数` as `大盘激励&插屏广告曝光次数`
from reva
order by reva.`日期`
