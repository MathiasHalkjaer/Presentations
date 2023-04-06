-- Proof of concept code, please be wary of using in production as-is

CREATE PROCEDURE [dbo].[SP_Reload_PBINextRefresh] @dataset uniqueidentifier, @workspace uniqueidentifier
AS
BEGIN
UPDATE rc
SET nextRefresh = rp.refreshDateTime
FROM pbiRefreshConfig rc
LEFT JOIN (
select refreshPolicy, min(date+cast(refreshTime as datetime)) as 'refreshDateTime' from pbiRefreshPolicies
CROSS JOIN (VALUES(cast(cast(DATEADD(hour,2,getdate()) as date)as datetime)),((cast(cast(DATEADD(hour,26,getdate()) as date)as datetime)))) t(date)
where date+cast(refreshTime as datetime) > DATEADD(hour,2,getdate())
group by refreshPolicy
) rp on rc.refreshPolicy = rp.refreshPolicy
where datasetID = @dataset and workspaceID = @workspace
END
GO
