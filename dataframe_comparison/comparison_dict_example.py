"""Reference example of a comparison dictionary.

This module defines a sample ``comparison_dictionary`` used to reconcile the
CRIS database against the combined NPS spreadsheet for the commercial tax
credit audit. It is included as documentation rather than runtime
configuration — copy and adapt it for new audits, or use it to understand the
shape :func:`~dataframe_comparison.compare_columns.run_comparison_and_reorder`
expects.

Dictionary shape:
    * Each top-level key is the name of a new reconciled column produced by
      the comparison.
    * The value is either:
        - ``None``: the key is a "stand-alone" identifier (e.g. ``NPSNumber``)
          carried through the pipeline without a comparison; it still
          participates in column ordering.
        - A dict with keys:
            ``columns`` (list[str, str])
                The two source column names (left, right) to compare. Order
                matters because ``default_first`` refers to the first entry.
            ``type`` (str)
                Either ``"string"`` or ``"numerical"`` — selects which
                comparison function runs.
            ``margin`` (int, numerical only)
                Percent tolerance used by
                :func:`~dataframe_comparison.compare_columns.compare_numerical_columns`.
                ``0`` requires an exact match; ``10`` accepts values within
                10% of their average.
            ``default_first`` (bool)
                When the two sources disagree (beyond ``margin`` for numeric
                comparisons), return the first column's value instead of the
                ``"DIFFERENT"`` sentinel.

The example below covers the typical mix: dollar-amount columns with a wider
margin, housing-unit counts with a tighter margin, and a few string columns
(uses, historic district name) where the comparison is exact.
"""

# Dictionary describing the comaparision between CRIS Database and the combined spreadsheet columns.
comparison_dictionary_CRIS_project_information = {
    'NPSNumber': None,
    'EstimatedRehabCost_PT2_2': {
        'columns': ['CRIS_PartTwoEstimatedRehabCost', 'EstimatedRehabCost_PT2'],
        'type': 'numerical',
        'margin': 10,
        'default_first': True
    },
    'EstimatedRehabCost_PT3_2': {
        'columns': ['CRIS_PartThreeEstimatedRehabCost', 'EstimatedRehabCost_PT3'],
        'type': 'numerical',
        'margin': 10,
        'default_first': True
    },
    'Total_Estimated_Cost_PT3_2': {
        'columns': ['CRIS_PartThreeTotalEstimatedProjectCost', 'Total_Estimated_Cost_PT3'],
        'type': 'numerical', 
        'margin': 10,
        'default_first': True
        
    },
    'FloorBefore': {
        'columns': ['CRIS_FloorBefore', 'Original_Floor'],
        'type': 'numerical',
        'margin': 10,
        'default_first': True
    },
    'FloorAfter': {
        'columns': ['CRIS_FloorAfter', 'Final_Floor_Both'],
        'type': 'numerical',
        'margin': 10,
        'default_first': True
    },
    'UsesAfter_2': {
        'columns': ['CRIS_UsesAfter', 'UsesAfter'],
        'type': 'string',
        'default_first': True
    },
    'P2_NumHousingUnitsAfter': {
        'columns': ['CRIS_P2_NumHousingUnitsAfter', 'P2_NumHousingUnitsRehabAfter'],
        'type': 'numerical',
        'margin': 5,
        'default_first': True
    },
    'P2_LowModIncomeUnitsAfter': {
        'columns': ['CRIS_P2_LowModIncomeUnitsAfter', 'P2_LowModIncomeHousingUnitsRehabAfter'],
        'type': 'numerical',
        'margin': 5,
        'default_first': True
    },
    'P3_NumHousingUnitsAfter': {
        'columns': ['CRIS_P3_NumHousingUnitsAfter', 'P3_NumHousingUnitsRehabAfter'],
        'type': 'numerical',
        'margin': 5,
        'default_first': True   
    },
    'P3_LowModIncomeUnitsAfter': {
        'columns': ['CRIS_P3_LowModIncomeUnitsAfter', 'P3_LowModIncomeHousingUnitsRehabAfter'],
        'type': 'numerical',
        'margin': 5,
        'default_first': True
    },
    'HistoricDistrictName': {
        'columns': ['CRIS_HistoricDistrictName', 'HistoricDistrict'],
        'type': 'string',
        'default_first': True
    },
    'NumPhases': {
        'columns': ['CRIS_NumPhases', 'TotalPhases'],
        'type': 'numerical',
        'margin': 5,
        'default_first': True
    }
}