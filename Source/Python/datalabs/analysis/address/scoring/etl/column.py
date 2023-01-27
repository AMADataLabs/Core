""" Address scoring column constants. """

INFO_COLUMNS = [
    'me',
    'entity_id',
    'comm_id',
    'address_key',
    'state_cd',
    'survey_date',
    'comments',
    'office_address_verified_updated',
    'status'
]


FILLMAX_COLUMNS = [
    'entity_comm_address_age',
    'humach_years_since_survey'
]


FILLNEG1_COLUMNS = [
    'license_this_state_years_since_expiration',
    'years_licensed_in_this_state'
]


FILL1_COLUMNS = [
    'humach_never_surveyed'
]
