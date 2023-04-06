-- Proof of concept code, nowhere near production-grade, please be wary of using in production as-is

CREATE TABLE [dbo].[pbiRefreshConfig](
	[datasetName] [nvarchar](50) NULL,
	[datasetID] [uniqueidentifier] NOT NULL,
	[workspaceID] [uniqueidentifier] NOT NULL,
	[nextRefresh] [datetime] NULL,
	[refreshPolicy] [nvarchar](50) NULL
)

CREATE TABLE [dbo].[pbiRefreshPolicies](
	[refreshPolicy] [nvarchar](50) NOT NULL,
	[refreshTime] [time](7) NULL
)

CREATE PROCEDURE [dbo].[SP_Reload_PBINextRefresh] @dataset uniqueidentifier, @workspace uniqueidentifier
AS
BEGIN
UPDATE rc
SET nextRefresh = rp.refreshDateTime
FROM pbiRefreshConfig rc
LEFT JOIN 
(
	SELECT refreshPolicy, min(date+cast(refreshTime as datetime)) AS 'refreshDateTime' FROM pbiRefreshPolicies
	CROSS JOIN 
	(
		VALUES(cast(cast(DATEADD(hour,2,getdate()) as date)as datetime)),
		((cast(cast(DATEADD(hour,26,getdate()) as date)as datetime)))
	) t(date)
	WHERE date+cast(refreshTime as datetime) > DATEADD(hour,2,getdate())
	GROUP BY refreshPolicy
) rp on rc.refreshPolicy = rp.refreshPolicy
WHERE datasetID = @dataset and workspaceID = @workspace
END
GO
