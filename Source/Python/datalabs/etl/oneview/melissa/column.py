"""Oneview Melissa Table Columns"""

ZIP_CODE_COLUMNS = {
    'id': 'id',
    'ZIP': 'zip_code',
    'STATE_CD': 'state',
    'CITY_CD': 'city',
    'ZIP_TYPE': 'type',
    'FIPS_CD': 'county_federal_information_processing',
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude',
    'MSA_CD': 'metropolitan_statistical_area',
    'PMSA_CD': 'primary_metropolitan_statistical_area'
}

COUNTY_COLUMNS = {
    'FIPS_CD': 'federal_information_processing_standard_code',
    'DESCRIPTION': 'county_name',
    'STATE_CD': 'state',
    'TIME_ZONE': 'time_zone',
    'COUNTY_TYPE': 'county_type',
    'COUNTY_SEAT': 'county_seat',
    'CNTY_NAME_TYPE': 'name_type',
    'ELEVATION': 'elevation',
    'PPH_NBR': 'person_per_household',
    'POPULATION': 'population',
    'AREA': 'area',
    'HSEHLD_NBR': 'households',
    'WHITE_NBR': 'white',
    'BLACK_NBR': 'black',
    'HISP_NBR': 'hispanic',
    'AVG_INCOME': 'average_income',
    'AVG_HOUSE_VAL': 'average_house'
}

AREA_CODE_COLUMNS = {
    'AREA_CD': 'area_code',
    'PREFIX': 'prefix',
    'LATITUDE': 'latitude',
    'LONGITUDE': 'longitude'
}

CENSUS_COLUMNS = {
    'ZIP': 'zip_code',
    'POPULATION': 'population',
    'URBAN': 'urban',
    'SUBURBAN': 'suburban',
    'FARM': 'farm',
    'NON_FARM': 'non_farm',
    'WHITE': 'white',
    'BLACK': 'black',
    'INDIAN': 'indian',
    'ASIAN': 'asian',
    'HAWAIIAN': 'hawaiian',
    'RACE_OTHER': 'race_other',
    'HISPANIC': 'hispanic',
    'AGE_0_4': 'age_0_to_4',
    'AGE_5_9': 'age_5_to_9',
    'AGE_10_14': 'age_10_to_14',
    'AGE_15_17': 'age_15_to_17',
    'AGE_18_19': 'age_18_to_19',
    'AGE_20': 'age_20',
    'AGE_21': 'age_21',
    'AGE_22_24': 'age_22_to_24',
    'AGE_25_29': 'age_25_to_29',
    'AGE_30_34': 'age_30_to_34',
    'AGE_35_39': 'age_35_to_39',
    'AGE_40_44': 'age_40_to_44',
    'AGE_45_49': 'age_45_to_49',
    'AGE_50_54': 'age_50_to_54',
    'AGE_55_59': 'age_55_to_59',
    'AGE_60_61': 'age_60_to_61',
    'AGE_62_64': 'age_62_to_64',
    'AGE_65_66': 'age_65_to_66',
    'AGE_67_69': 'age_67_to_69',
    'AGE_70_74': 'age_70_to_74',
    'AGE_75_79': 'age_75_to_79',
    'AGE_80_84': 'age_80_to_84',
    'AGE_85_PLS': 'age_85_plus',
    'EDU_LESS_9': 'education_below_9',
    'EDU_9_12': 'education_9_to_12',
    'EDU_HIGH_SC': 'education_high_school',
    'EDU_SOME_CL': 'education_some_college',
    'EDU_ASSOC': 'education_association',
    'EDU_BACH': 'education_bachelor',
    'EDU_PROF': 'education_professional',
    'HH_INCOME': 'household_income',
    'PC_INCOME': 'per_person_income',
    'HOUSE_VAL': 'house_value'
}

CORE_BASED_STATISTICAL_AREA_COLUMNS = {
    'ZIP_CBSA_DIVISION': 'code',
    'CBSA_OR_DIV': 'type',
    'LOCATION_TITLE': 'title',
    'LEVEL_MSA': 'level',
    'STATUS_1_OR_2': 'status'
}

ZIP_CODE_CORE_BASED_STATISTICAL_AREA_COLUMNS = {
    'ZIP': 'zip_code',
    'CBSA': 'core_based_statistical_area',
    'DIV': 'division'
}

METROPOLITAN_STATISTICAL_AREA_COLUMNS = {
    'MSA_CD': 'code',
    'MSA_TYPE': 'type',
    'DESCRIPTION': 'name',
    'CMSA_CD': 'consolidated_metropolitan_statistical_area',
    'POPULATION': 'population'
}
