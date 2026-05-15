pivot_dict = {

    'SUNY.sql': {
        'index' : 'ProjectYear',
        'columns' : 'Finding',
        'values' : 'NumProjects',
        'consultations_only': True,
        'can_normalize': True,
        'normalized_values': 'ProjPercent'
    },

    'SUCF.sql': {
        'index' : 'ProjectYear',
        'columns' : 'Finding',
        'values' : 'NumProjects',
        'consultations_only': True,
        'can_normalize': True,
        'normalized_values': 'ProjPercent'
    },

    'SUCF_SUNY_all.sql': {
        'index' : 'ProjectYear',
        'columns' : 'AgencyCode',
        'values' : 'NumProjects',
        'consultations_only': True
    },
    'MTA/MTA_Promects_By_Year_Finding_Area.sql': {
        'index' : 'ProjectYear',
        'columns' : 'Finding',
        'values' : 'NumProjects',
        'consultations_only': True,
        'can_normalize': True,
        'normalized_values': 'ProjPercent'
    },

    'MTA/MTA_Projects_By_Year_and_Geography.sql': {
        'index' : 'ProjectYear',
        'columns' : 'Geography',
        'values' : 'NumProjects',
        'consultations_only': True,
        'can_normalize': True,
        'normalized_values': 'ProjPercent'
    },
    'MTA/MTA_Projects_By_Year_and_Finding_NYC.sql': {
        'index' : 'ProjectYear',
        'columns' : 'Finding',
        'values' : 'NumProjects',
        'consultations_only': True,
        'can_normalize': True,
        'normalized_values': 'ProjPercent'
    },
    'MTA/MTA_Projects_By_Year_and_Finding_Long_Island.sql': {
        'index' : 'ProjectYear',
        'columns' : 'Finding',
        'values' : 'NumProjects',
        'consultations_only': True,
        'can_normalize': True,
        'normalized_values': 'ProjPercent'
    },
}  