""" Column maps for marketing data """

ADHOC_COLUMNS = {
    'CUSTOMER_ID' : 'CUSTOMER_ID',
    'NAME' : 'NAME',
    'BUSTITLE' : 'BUSTITLE',
    'BUSNAME' : 'BUSNAME',
    'ADDR1' : 'ADDR1',
    'ADDR2' : 'ADDR2',
    'ADDR3' : 'ADDR3',
    'CITY' : 'CITY',
    'STATE' : 'STATE',
    'ZIP' : 'ZIP',
    'COUNTRY' : 'COUNTRY',
    'EMAIL' : "BEST_EMAIL",
    'DAY_PHONE' : 'DAY_PHONE',
    'EVENING_PHONE' : 'EVENING_PHONE',
    'INDUSTRY_DESC' : 'INDUSTRY_DESC',
    'File_Name' : 'File_Name'
}

AIMS_COLUMNS = {
    '#AMA_Membership_Flag': 'MEMBERFLAG',
    'ME_Nbr': 'ME_Nbr',
    'Gender' : "GENDER",
    'Prim_Spec_Cd' : "AIMS_PRIMSPC",
    'Sec_Spec_Cd' : "AIMS_SECSPC",
    'Do_no_rent_flag' : "SUP_DNRFLAG",
    'Do_not_mail/email_flag' : "SUP_DNMFLAG",
    'Preferred_Email': 'BEST_EMAIL'
}

LIST_OF_LISTS_COLUMNS = {
    'LIST NUMBER' : 'LIST NUMBER',
    'CHANGED STATUS' : 'CHANGED STATUS',
    'STATUS' : 'STATUS',
    'LIST SOURCE KEY': 'LISTKEY',
    'LIST NAME' : 'LIST NAME',
    'SOURCE' : 'SOURCE'
}

MERGE_LIST_OF_LISTS_COLUMNS = {
    "CUSTOMER_ID",
    "ME_Nbr",
    "LIST NUMBER",
    "CHANGED STATUS",
    "STATUS",
    "LIST NAME",
    "SOURCE",
    "File_Name"
}

JOIN_LISTKEYS_COLUMNS = {
    "LISTKEY_y" : "LISTKEY_COMBINED",
    "LISTKEY_x" : "LISTKEY"
}

INVALID_EMAILS_COLUMNS = {
    'FINDING',
    'COMMENT',
    'COMMENT_CODE',
    'SUGG_EMAIL',
    'SUGG_COMMENT',
    'flag'
}
