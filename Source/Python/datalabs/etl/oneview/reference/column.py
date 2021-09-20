"""OneView Reference Table Columns"""
MPA_COLUMNS = {
    'MPA_CD': 'id',
    'DESC': 'description',
}
TOP_COLUMNS = {
    'TOP_CD': 'id',
    'DESC': 'description'
}
PE_COLUMNS = {
    'EMPLOYER_CD': 'id',
    'DESC': 'description'
}
CBSA_COLUMNS = {
    'CBSA Code': 'id',
    'CBSA Name': 'description'
}
SPECIALTY_MERGED_COLUMNS = {
    'SPEC_CD': 'id',
    'DESC': 'description'
}
FIPSC_COLUMNS = {
    'id': 'id',
    'State Code (FIPS)': 'state',
    'County Code (FIPS)': 'county',
    'Area Name (including legal/statistical area description)': 'description'
}
PROVIDER_AFFILIATION_GROUP = {
    'id': 'id',
    'description': 'description'
}
PROVIDER_AFFILIATION_TYPE = {
    'id': 'id',
    'description': 'description'
}
PROFIT_STATUS = {
    'id': 'id'
}
OWNER_STATUS = {
    'id': 'id'
}
COT_SPECIALTY = {
    'COT_SPECIALTY_ID': 'id',
    'COT_SPECIALTY': 'description',
}
COT_FACILITY = {
    'COT_FACILITY_TYPE_ID': 'id',
    'COT_FACILITY_TYPE': 'description',
}
STATE = {
    'STATE_ID': 'id',
    'SRC_STATE_CD': 'code',
    'DESC': 'description'
}
