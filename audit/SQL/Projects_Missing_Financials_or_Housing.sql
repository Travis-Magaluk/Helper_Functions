/*

This query looks across all commercial tax credit projects and returns the following: 
    - Project Number
    - Project Year (Based on the Project Number)
    - NPS Project Number
    - Tax Credit Commercial ID
    - Latest Decision Part 
    - Missing Part 2 Financials (Boolean)
    - Missing Part 2 Housing (Boolean)
    - Missing Part 3 Financials (Boolean)
    - Missing Part 3 Housing (Boolean)

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