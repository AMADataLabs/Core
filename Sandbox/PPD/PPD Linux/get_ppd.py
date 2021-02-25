# Garrett Lappe
#
# get_ppd(ppd_filename) - returns latest (default) or specific PPD file as DataFrame, 
# specified by file name in baseline folder.


import pandas as pd
import os

# returns the name of the latest PPD raw data file from the U: drive
#   WILL NEED TO BE CHANGED IN 2020
def get_latest_ppd_filename():
    ppd_dir = "/mnt/u/Source Files/Data Analytics/Baseline/data/"
    files = os.listdir(ppd_dir)
    ppds = []
    
    # compile a list of the valid PPD files
    for f in files:
        if 'PhysicianProfessionalDataFile_2019' in f:  ################## change to 2020 next year #########
            ppds.append(f)
            
    # sort the list in descending order (file name indicates date, desc = newest first)
    ppds.sort(reverse=True)
    
    # take the first one (newest)
    latest = ppds[0]
    
    return latest


# returns a DataFrame of ppd
#   latest PPD returned by default
#   Specific PPD can be returned by passing the name of the file in the baseline folder--NOT the full file path.
def get_ppd(ppd_filename=get_latest_ppd_filename()):
    
    # edit file path / name as needed to grab desired PPD version
    ppd_path = "/mnt/u/Source Files/Data Analytics/Baseline/data/{}".format(ppd_filename)

    cols = [
        'ME',
        'RECORD_ID',
        'UPDATE_TYPE',
        'ADDRESS_TYPE',
        'MAILING_NAME',
        'LAST_NAME',
        'FIRST_NAME',
        'MIDDLE_NAME',
        'SUFFIX',
        'MAILING_LINE_1',
        'MAILING_LINE_2',
        'CITY',
        'STATE',
        'ZIP',
        'SECTOR',
        'CARRIER_ROUTE',
        'ADDRESS_UNDELIVERABLE_FLAG',
        'FIPS_COUNTY',
        'FIPS_STATE',
        'PRINTER_CONTROL_CODE',
        'PC_ZIP',
        'PC_SECTOR',
        'DELIVERY_POINT_CODE',
        'CHECK_DIGIT',
        'PRINTER_CONTROL_CODE_2',
        'REGION',
        'DIVISION',
        'GROUP',
        'TRACT',
        'SUFFIX_CENSUS',
        'BLOCK_GROUP',
        'MSA_POPULATION_SIZE',
        'MICRO_METRO_IND',
        'CBSA',
        'CBSA_DIV_IND',
        'MD_DO_CODE',
        'BIRTH_YEAR',
        'BIRTH_CITY',
        'BIRTH_STATE',
        'BIRTH_COUNTRY',
        'GENDER',
        'TELEPHONE_NUMBER',
        'PRESUMED_DEAD_FLAG',
        'FAX_NUMBER',
        'TOP_CD',
        'PE_CD',
        'PRIM_SPEC_CD',
        'SEC_SPEC_CD',
        'MPA_CD',
        'PRA_RECIPIENT',
        'PRA_EXP_DT',
        'GME_CONF_FLG',
        'FROM_DT',
        'TO_DT',
        'YEAR_IN_PROGRAM',
        'POST_GRADUATE_YEAR',
        'GME_SPEC_1',
        'GME_SPEC_2',
        'TRAINING_TYPE',
        'GME_INST_STATE',
        'GME_INST_ID',
        'MEDSCHOOL_STATE',
        'MEDSCHOOL_ID',
        'MEDSCHOOL_GRAD_YEAR',
        'NO_CONTACT_IND',
        'NO_WEB_FLAG',
        'PDRP_FLAG',
        'PDRP_START_DT',
        'POLO_MAILING_LINE_1',
        'POLO_MAILING_LINE_2',
        'POLO_CITY',
        'POLO_STATE',
        'POLO_ZIP',
        'POLO_SECTOR',
        'POLO_CARRIER_ROUTE',
        'MOST_RECENT_FORMER_LAST_NAME',
        'MOST_RECENT_FORMER_MIDDLE_NAME',
        'MOST_RECENT_FORMER_FIRST_NAME',
        'NEXT_MOST_RECENT_FORMER_LAST',
        'NEXT_MOST_RECENT_FORMER_MIDDLE',
        'NEXT_MOST_RECENT_FORMER_FIRST'
    ]

    # read the file and create a DataFrame
    ppd = pd.read_csv(ppd_path, names=cols, sep='|', encoding='IBM437', index_col=False, dtype=object)

    return ppd