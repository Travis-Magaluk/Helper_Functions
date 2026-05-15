# Multi-query SQL module used by audit scripts.
# Each variable below contains a multi-line SQL query string. Comments were added
# (Python comments above each variable and SQL block comments inside the strings)
# to explain intent, outputs, CTEs, mappings, assumptions, and edge cases.

# decisions_sql
# Purpose: Return project-level decisions for commercial tax credit projects,
# mapping numeric TaxCreditDecisionId values to human-readable labels.
decisions_sql = """
/*
Return a simple list of decisions for commercial tax credit projects.

Behavior:
- Maps numeric TaxCreditDecisionId values to human-readable Decision labels using CASE.
  - Approve: an approved decision (ids: 1, 2, 4, 6, 7, 8, 12, 13, 9, 32)
  - CA: conditionally approved (id: 10)
  - Deny: denied (ids: 3, 5, 11, 14, 33)
  - OTHER: any decision id outside the specified lists
- Joins:
  - INNER JOIN with `lutTaxCreditDecision` to use lookup table for part mapping (ltcd)
  - LEFT JOIN to `tblTaxCreditCommercial` to include NPSProjectNumber if available. 
  - - NPSProject number is needed to join to NPS Quarterly Reports. 
- Filters:
  - Only active decisions (ttcd.Active = 1)
- Ordering:
  - Results ordered by NPSProjectNumber

Notes:
- Keep mapping lists updated if new decision ids are introduced.
*/
    SELECT NPSProjectNumber, 
    CASE
        WHEN ttcd.TaxCreditDecisionId IN (1, 2, 4, 6, 7, 8, 12, 13, 9, 32) THEN 'Approve'
        WHEN ttcd.TaxCreditDecisionId IN (10) THEN 'CA'
        WHEN ttcd.TaxCreditDecisionId IN (3, 5, 11, 14, 33) THEN 'Deny'
        ELSE 'OTHER'
        END AS Decision,
    DateDecision,
    TaxCreditPart
    FROM tblTaxCreditCommercialDecision ttcd
    INNER JOIN lutTaxCreditDecision ltcd
        ON ttcd.TaxCreditDecisionId = ltcd.TaxCreditDecisionId
    LEFT JOIN tblTaxCreditCommercial ttcc
        ON ttcc.TaxCreditCommercialId = ttcd.TaxCreditCommercialId
    WHERE ttcd.Active = 1
    ORDER BY NPSProjectNumber
    """


# nps_number_pr_mapping
# Purpose: Map external NPSProjectNumber to internal ProjectNum for commercial tax credit projects.
nps_number_pr_mapping = """
/*
Return a mapping between NPSProjectNumber and ProjectNum.

Notes:
- If multiple projects share the same NPSProjectNumber this will return multiple rows.
*/
    SELECT 
        NPSProjectNumber, 
        ProjectNum
    FROM tblProject tp
    INNER JOIN tblTaxCreditCommercial ttcc
        ON tp.TaxCreditCommercialId = ttcc.TaxCreditCommercialId
    """


# projects_missing_financials_or_housing
# Purpose: Find commercial tax credit projects whose latest relevant decision implies Part 2/3
#          data is required but some Part 2/3 financial or housing fields are missing.
projects_missing_financials_or_housing = """


/*

This query looks across all commercial tax credit projects and returns the following: 
    - Project Number (ProjectNum)
    - Project Year (four_digit_year, derived from ProjectNum)
    - NPS Project Number (NPSProjectNumber)
    - Tax Credit Commercial ID (TaxCreditCommercialId)
    - Latest Decision Part (LatestDecisionPart)
    - Missing Part 2 Financials (MissingPart2_Financials, 1/0)
    - Missing Part 2 Housing (MissingPart2_Housing, 1/0)
    - Missing Part 3 Financials (MissingPart3_Financials, 1/0)
    - Missing Part 3 Housing (MissingPart3_Housing, 1/0)

High-level flow (CTE breakdown):
1) FilteredDecisions:
   - Restricts to a specific set of TaxCreditDecisionId values and maps them to 'Approve', 'Deny', or 'CA'
     taking into account which TaxCreditPart (1/2/3) the decision refers to.
   - Important: mapping differs by part (e.g., Part 2 approve = id 9, while Part 1 has a broader set).

   Mapping summary used in this CTE:
   - Part 1: Approve ids (1,2,4,6,7,8,32); Deny ids (3,5,33)
   - Part 2: Approve id 9; CA id 10; Deny id 11
   - Part 3: Approve ids (12,13); Deny id 14

2) RankedDecisions:
   - Adds ROW_NUMBER() partitioned by (TaxCreditCommercialId, TaxCreditPart) ordered by DateDecision ASC.
   - Management requested earliest decision per part; rn = 1 therefore selects the earliest decision per part.

3) EarliestDecisions:
   - Keeps only the earliest decision per (TaxCreditCommercialId, TaxCreditPart).

4) Pivoted:
   - Pivots earliest per-part decisions into columns Part1Decision/Date, Part2Decision/Date, Part3Decision/Date.

5) Sub_Final:
   - Joins pivoted decision data back to `tblTaxCreditCommercial` and `tblProject`.
   - Uses COALESCE in the order Part3, Part2, Part1 to determine LatestDecision and LatestDecisionDate.
   - Determines LatestDecisionPart by presence of non-null Part3/Part2/Part1 decision.

6) Final:
   - Parses `ProjectNum` to compute a 4-digit year (simple two-digit heuristic).
   - Flags missing Part 2/3 financial and housing fields depending on LatestDecisionPart.
   - Only returns projects with missing flags (any of the missing flags = 1) and four_digit_year > 2014.

Important assumptions and caveats:
- This intentionally uses ORDER BY DateDecision ASC to choose the earliest decision per part (management requested this).
- If DateDecision is NULL, ordering behavior may be unexpected; consider filtering or coalescing if needed.
- The four_digit_year calculation assumes ProjectNum's first two characters encode the year; verify format before changing.
- The missing-field checks are strict IS NULL checks on specific tc.* columns; if empty strings or sentinel values are used
  in your data, adapt checks accordingly.

*/
WITH FilteredDecisions AS (
    SELECT
        tcd.TaxCreditCommercialId,
        tcd.TaxCreditDecisionId,
        ltcd.TaxCreditPart,
        tcd.DateDecision,
        CASE
            -- Part 1
            WHEN ltcd.TaxCreditPart = 1 AND tcd.TaxCreditDecisionId IN (1,2,4,6,7,8, 32) THEN 'Approve'
            WHEN ltcd.TaxCreditPart = 1 AND tcd.TaxCreditDecisionId IN (3,5, 33) THEN 'Deny'
            -- Part 2
            WHEN ltcd.TaxCreditPart = 2 AND tcd.TaxCreditDecisionId = 9 THEN 'Approve'
            WHEN ltcd.TaxCreditPart = 2 AND tcd.TaxCreditDecisionId = 10 THEN 'CA'
            WHEN ltcd.TaxCreditPart = 2 AND tcd.TaxCreditDecisionId = 11 THEN 'Deny'
            -- Part 3
            WHEN ltcd.TaxCreditPart = 3 AND tcd.TaxCreditDecisionId IN (12,13) THEN 'Approve'
            WHEN ltcd.TaxCreditPart = 3 AND tcd.TaxCreditDecisionId = 14 THEN 'Deny'
            ELSE NULL
        END AS PartDecision
    FROM tblTaxCreditCommercialDecision tcd
    INNER JOIN lutTaxCreditDecision ltcd
        ON tcd.TaxCreditDecisionId = ltcd.TaxCreditDecisionId
    WHERE (tcd.TaxCreditDecisionId IN (1,2,3,4,5,6,7,8,9,10,11,12,13,14,32,33))
    AND tcd.Active = 1
),
RankedDecisions AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY TaxCreditCommercialId, TaxCreditPart ORDER BY DateDecision ASC) AS rn
    FROM FilteredDecisions
),
EarliestDecisions AS (
    SELECT *
    FROM RankedDecisions
    WHERE rn = 1
),
Pivoted AS (
    SELECT
        ed.TaxCreditCommercialId,
        MAX(CASE WHEN ed.TaxCreditPart = 1 THEN ed.PartDecision END) AS Part1Decision,
        MAX(CASE WHEN ed.TaxCreditPart = 1 THEN ed.DateDecision END) AS Part1DecisionDate,
        MAX(CASE WHEN ed.TaxCreditPart = 2 THEN ed.PartDecision END) AS Part2Decision,
        MAX(CASE WHEN ed.TaxCreditPart = 2 THEN ed.DateDecision END) AS Part2DecisionDate,
        MAX(CASE WHEN ed.TaxCreditPart = 3 THEN ed.PartDecision END) AS Part3Decision,
        MAX(CASE WHEN ed.TaxCreditPart = 3 THEN ed.DateDecision END) AS Part3DecisionDate
    FROM EarliestDecisions ed
    GROUP BY ed.TaxCreditCommercialId
),
Sub_Final as (SELECT
    ttc.NPSProjectNumber,
    ttc.TaxCreditCommercialId,
    tp.ProjectNum,
    p.Part1Decision,
    p.Part1DecisionDate,
    p.Part2Decision,
    p.Part2DecisionDate,
    p.Part3Decision,
    p.Part3DecisionDate,

    -- Latest non-null decision in order: 3, 2, 1
    COALESCE(p.Part3Decision, p.Part2Decision, p.Part1Decision) AS LatestDecision,
    COALESCE(p.Part3DecisionDate, p.Part2DecisionDate, p.Part1DecisionDate) AS LatestDecisionDate,

    -- Part from which the latest decision came
    CASE
        WHEN p.Part3Decision IS NOT NULL THEN 'Part 3'
        WHEN p.Part2Decision IS NOT NULL THEN 'Part 2'
        WHEN p.Part1Decision IS NOT NULL THEN 'Part 1'
        ELSE NULL
    END AS LatestDecisionPart

FROM tblTaxCreditCommercial ttc
LEFT JOIN Pivoted p ON ttc.TaxCreditCommercialId = p.TaxCreditCommercialId and ttc.Active = 1
LEFT JOIN tblProject tp 
    ON ttc.TaxCreditCommercialId = tp.TaxCreditCommercialId AND tp.Active = 1),

Final AS (
SELECT
Sub_Final.ProjectNum,
CASE
        WHEN CAST(SUBSTRING(Sub_Final.ProjectNum, 1, 2) AS INT) <= 25 THEN 2000 + CAST(SUBSTRING(Sub_Final.ProjectNum, 1, 2) AS INT)
        ELSE 1900 + CAST(SUBSTRING(Sub_Final.ProjectNum, 1, 2) AS INT)
    END AS four_digit_year,
Sub_Final.NPSProjectNumber, 
Sub_Final.TaxCreditCommercialId, 
Sub_Final.LatestDecisionPart,
CASE
    WHEN Sub_Final.LatestDecisionPart IN ('Part 2', 'Part 3')  AND (
        tc.PartTwoEstimatedRehabCost IS NULL
        )
    THEN 1
    ELSE 0
END AS MissingPart2_Financials,
CASE
    WHEN Sub_Final.LatestDecisionPart IN ('Part 2', 'Part 3')  AND (
        tc.PartTwoNumHousingUnitsRehabBefore IS NULL OR
        tc.PartTwoNumHousingUnitsRehabAfter IS NULL OR 
        tc.PartTwoNumLowModIncomeHousingUnitsRehabBefore IS NULL OR
        tc.PartTwoNumLowModIncomeHousingUnitsRehabAfter IS NULL
        )
    THEN 1
    ELSE 0
END AS MissingPart2_Housing,
CASE	
    WHEN Sub_Final.LatestDecisionPart = 'Part 3' AND (
        tc.PartThreeEstimatedRehabCost IS NULL OR 
        tc.PartThreeTotalEstimatedProjectCost IS NULL)
    THEN 1
    ELSE 0
END AS MissingPart3_Financials,
CASE	
    WHEN Sub_Final.LatestDecisionPart = 'Part 3' AND (
        tc.PartThreeNumHousingUnitsRehabBefore IS NULL OR 
        tc.PartThreeNumHousingUnitsRehabAfter IS NULL OR 
        tc.PartThreeNumLowModIncomeHousingUnitsRehabBefore IS NULL OR 
        tc.PartThreeNumLowModIncomeHousingUnitsRehabAfter IS NULL
        )
    THEN 1
    ELSE 0
END AS MissingPart3_Housing
FROM Sub_Final
INNER JOIN tblTaxCreditCommercial tc
    ON Sub_Final.TaxCreditCommercialId = tc.TaxCreditCommercialId
    AND tc.Active = 1)

SELECT * FROM Final
WHERE (MissingPart2_Financials = 1 
OR MissingPart2_Housing = 1
OR MissingPart3_Financials = 1
OR MissingPart3_Housing = 1)
AND four_digit_year > 2014
"""


# duplicate_NPS_project_numbers
# Purpose: Identify NPSProjectNumber values that are associated with multiple internal projects.
duplicate_NPS_project_numbers = """

/*
Identify NPSProjectNumber values that appear multiple times across projects.

Flow:
- BasePull: selects ProjectNum, ProjectName, NPSProjectNumber and computes a window COUNT per NPSProjectNumber.
- Final select filters rows where the count > 1 (i.e., duplicate NPS numbers).
*/
WITH BasePull AS

(SELECT 
tp.ProjectNum,
tp.ProjectName,
ttcc.NPSProjectNumber,
COUNT(NPSProjectNumber) OVER (PARTITION BY NPSProjectNumber) as NPSNumber_Count
FROM tblTaxCreditCommercial ttcc
INNER JOIN tblProject tp
    ON ttcc.TaxCreditCommercialId = tp.TaxCreditCommercialId
)

SELECT * FROM BasePull
WHERE NPSNumber_Count > 1

"""


# nonspatial_usn
# Purpose: Find USN records with no spatial point in the USNBLDGPOINT table and join attachments and HTC projects.
nonspatial_usn = """

/*
This query has two main parts:

1) nonspatial_USN CTE:
   - Selects USNNum and descriptive fields from `vwUSNInfo`.
   - Left joins to `CRISGIS.dbo.USNBLDGPOINT` to identify USNs with no point geometry (gu.OBJECTID IS NULL).
   - Left joins attachment linking tables to compute AttachmentCount (only counts ta.Active = 1).
   - Filters for vu.USNTypeId = 2 (domain-specific; adjust as needed).
   - Groups by USN attributes to get a per-USN AttachmentCount.

2) HTC_Projects_and_USNs CTE:
   - Finds HTC projects linked to USNs via xrfProjectUSN and joins in project and USN lookup metadata.

Final select:
- Joins HTC_Projects_and_USNs to nonspatial_USN on USNNum so you can see projects associated with non-spatial USNs.

Notes and caveats:
- Cross-database references (CRIS.dbo, CRISGIS.dbo) assume appropriate permissions and server context.
*/
WITH nonspatial_USN as (SELECT vu.USNNum, vu.USNName, vu.Counties, vu.MCDs, vu.Eligibility
    ,SUM(CASE WHEN ta.AttachmentId IS NOT NULL THEN 1 ELSE 0 END) AttachmentCount
FROM CRIS.dbo.vwUSNInfo vu
    LEFT JOIN CRISGIS.dbo.USNBLDGPOINT gu
        ON vu.USNNum = gu.USNNum
    LEFT JOIN CRIS.dbo.xrfUSNAttachment xua
        ON vu.USNId = xua.USNId
    LEFT JOIN CRIS.dbo.tblAttachment ta
        ON xua.AttachmentId = ta.AttachmentId
        AND ta.Active = 1
WHERE gu.OBJECTID IS NULL
    AND vu.USNTypeId = 2
GROUP BY vu.USNNum, vu.USNName, vu.Counties, vu.MCDs, vu.Eligibility),

HTC_Projects_and_USNs as (
    SELECT 
    ProjectNum,
    ProjectName, 
    tu.USNId, 
    USNNum,
    lut.USNType
    FROM tblTaxCreditCommercial ttcc
    INNER JOIN tblProject tp
        ON ttcc.TaxCreditCommercialId = tp.TaxCreditCommercialId
    INNER JOIN xrfProjectUSN xpu
        ON tp.ProjectId = xpu.ProjectId 
        AND xpu.Active = 1
    INNER JOIN tblUSN tu
        ON xpu.USNId= tu.USNId
    INNER JOIN lutUSNType lut
        ON tu.USNTypeId = lut.USNTypeId
    
)

SELECT * FROM HTC_Projects_and_USNs projects
INNER JOIN nonspatial_USN nonspatial
    ON projects.USNNum = nonspatial.USNNum
"""