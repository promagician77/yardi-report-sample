/*===========================================================================
  cu_rpt_AgedDelinquency
  Aged receivables by property, aged against an as-of date.

  Written for Yardi Voyager (SQL Server / SSRS). Two things make it safe to
  hand to a client:

  1. SECURITY. Voyager enforces property access in the application. A report
     that reads artran directly inherits none of it, so the user's property
     list is joined in and nothing can escape it. @CurrentUser is supplied by
     the SSRS report as User!UserID, not typed by the person running it.

  2. UPGRADES. Objects are prefixed cu_ so a Voyager upgrade leaves them in
     place, and the query reads the documented columns rather than whatever
     happens to be adjacent in the table today.

  Parameters
     @AsOfDate     date   aging is measured back from here
     @CurrentUser  nvarchar(64)  session user, from SSRS User!UserID
     @hProperty    int    optional single property, NULL for the full list
===========================================================================*/
CREATE PROCEDURE dbo.cu_rpt_AgedDelinquency
    @AsOfDate     date,
    @CurrentUser  nvarchar(64),
    @hProperty    int = NULL
AS
BEGIN
    SET NOCOUNT ON;

    /* The user's entitled properties. Everything downstream joins through
       this, so an omitted WHERE clause cannot widen the result set. */
    ;WITH SecuredProperty AS (
        SELECT  p.hMy, p.sCode, p.sName
        FROM    dbo.property     p
        JOIN    dbo.userproperty up ON up.hProperty = p.hMy
        JOIN    dbo.cuser        u  ON u.hMy        = up.hUser
        WHERE   u.sUserName = @CurrentUser
          AND  (@hProperty IS NULL OR p.hMy = @hProperty)
    )
    SELECT
        p.sCode                         AS PropertyCode,
        p.sName                         AS PropertyName,
        t.sName                         AS TenantName,
        un.sUnitCode                    AS UnitCode,
        SUM(CASE WHEN DATEDIFF(day, a.dtPost, @AsOfDate) <=  30
                 THEN a.cOpenAmount ELSE 0 END)  AS Current_0_30,
        SUM(CASE WHEN DATEDIFF(day, a.dtPost, @AsOfDate) BETWEEN 31 AND 60
                 THEN a.cOpenAmount ELSE 0 END)  AS Days_31_60,
        SUM(CASE WHEN DATEDIFF(day, a.dtPost, @AsOfDate) BETWEEN 61 AND 90
                 THEN a.cOpenAmount ELSE 0 END)  AS Days_61_90,
        SUM(CASE WHEN DATEDIFF(day, a.dtPost, @AsOfDate) >   90
                 THEN a.cOpenAmount ELSE 0 END)  AS Days_Over_90,
        SUM(a.cOpenAmount)                       AS TotalDue
    FROM        dbo.artran     a
    JOIN        SecuredProperty p  ON p.hMy  = a.hProperty
    JOIN        dbo.tenant      t  ON t.hMy  = a.hTenant
    JOIN        dbo.unit        un ON un.hMy = t.hUnit
    WHERE       a.cOpenAmount > 0
      AND       a.iType       = 1          /* charges only, payments excluded */
      AND       a.dtPost     <= @AsOfDate
    GROUP BY    p.sCode, p.sName, t.sName, un.sUnitCode
    HAVING      SUM(a.cOpenAmount) > 0
    ORDER BY    p.sName, t.sName;
END
GO
