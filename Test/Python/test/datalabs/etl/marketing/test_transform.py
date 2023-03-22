""" source: datalabs.etl.marketing.aggregate.transform """
import pickle

import pandas as pd
import pytest

from datalabs.etl.marketing.aggregate.transform import InputDataCleanerTask


# pylint: disable=redefined-outer-name, protected-access
def test_input_data_cleaner_transformer_extract_all_files(pickled_data):
    transformer = InputDataCleanerTask({}, pickled_data)

    named_files_data = pickle.loads(pickled_data[0])

    named_files_list = ['2023ViVESpeakers_03142023.csv',
            'CPT Dev Program Sign Ups Since 021022_20230316.csv',
            'CPT Intl _CU_INTL.csv',
            'mbr_info_20230101.dat',
            'AMA List of Lists_20230317.csv',
            'SFMC_FlatFile_2023-03-16.txt'
    ]

    for index,named_file in enumerate(named_files_data):
        assert ( named_files_list[index] in named_file[0]) is True

    input_files = transformer._extract_files(named_files_data)

    assert len(input_files) == 6


# pylint: disable=redefined-outer-name, protected-access
def test_input_data_cleaner_transformer_clean_data(pickled_data):
    transformer = InputDataCleanerTask({}, pickled_data)

    named_files_data = pickle.loads(pickled_data[0])

    input_files = transformer._extract_files(named_files_data)

    input_adhoc_files = transformer._merge_adhoc_data(input_files)

    assert(isinstance(input_adhoc_files, pd.DataFrame)) is True

    read_input_files = transformer._read_input_data(input_files)

    assert(isinstance(read_input_files.adhoc, pd.DataFrame)) is True
    assert(isinstance(read_input_files.aims, pd.DataFrame)) is True
    assert(isinstance(read_input_files.list_of_lists, pd.DataFrame)) is True
    assert(isinstance(read_input_files.flatfile, pd.DataFrame)) is True

    clean_input_files = transformer._clean_input_data(read_input_files)
    # pylint: disable=line-too-long
    assert( list(clean_input_files.adhoc.columns )) == ['CUSTOMER_ID', 'NAME', 'BUSTITLE', 'BUSNAME', 'ADDR1', 'ADDR2', 'ADDR3', 'CITY', 'STATE', 'ZIP', 'COUNTRY', 'BEST_EMAIL', 'DAY_PHONE', 'EVENING_PHONE', 'INDUSTRY_DESC']
    # pylint: disable=line-too-long
    assert(list(clean_input_files.aims.columns )) == ['MEMBERFLAG', 'ME_Nbr', 'GENDER', 'AIMS_PRIMSPC', 'AIMS_SECSPC', 'SUP_DNRFLAG', 'SUP_DNMFLAG', 'BEST_EMAIL', 'PHYSICIANFLAG']
    # pylint: disable=line-too-long
    assert(list(clean_input_files.list_of_lists.columns)) == ['LIST NUMBER', 'CHANGED STATUS', 'STATUS', 'LISTKEY', 'LIST NAME', 'SOURCE']

    output_files = transformer.run( )

    assert len(output_files) == 4


# pylint: disable=redefined-outer-name, protected-access
def test_empty_input_data_cleaner_transformer(empty_pickled_data):
    transformer = InputDataCleanerTask({}, empty_pickled_data)
    output_files = transformer.run( )

    assert (output_files) is None


# pylint: disable=line-too-long
@pytest.fixture
def pickled_data():
    return [b'\x80\x04\x95\xcc\x12\x00\x00\x00\x00\x00\x00]\x94(\x8cs/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/Adhoc_1/2023ViVESpeakers_03142023.csv\x94B\x0f\x01\x00\x00\xef\xbb\xbfCUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC\r\n,Abby Levy,Managing Partner,Primetime Partners,13310 Rhodine Rd,,,Riverview,FL,33579,United States,abby@primetimepartners.com,,,2023 ViVE Speakers\r\n\x94\x86\x94\x8c\x88/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/Adhoc_1/CPT Dev Program Sign Ups Since 021022_20230316.csv\x94C\xaa\xef\xbb\xbfCUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC\r\n97, ,,,,,,,,,,drs26@cornell.edu,,,Health-tech\r\n\x94\x86\x94\x8ck/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/Adhoc_1/CPT Intl _CU_INTL.csv\x94C\xfa\xef\xbb\xbfCUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC\r\n,Tathagata Ray,"Manager, Business Intelligence",Sonic Incytes Medical Corp,,,,,,,Canada,tathagata@sonicincytes.com,,,CPT Intl\r\n\x94\x86\x94\x8cj/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/AIMS_1/mbr_info_20230101.dat\x94B\xe7\x03\x00\x00#AMA_Membership_Flag|First_Name|Middle_Name|Last_Name|Degree_Type|ME_Nbr|Gender|Birth_Yr|TOP|PE_Code|MPA_Code|Prim_Spec_Cd|Sec_Spec_Cd|No_Contact_Flag|Do_no_rent_flag|do_not_solicit|Do_not_mail/email_flag|PPMA_Addr1|PPMA_Addr2|PPMA_Suite|PPMA_City|PPMA_State|PPMA_Zip|PPMA_plus4|POLO_Addr1|POLO_Addr2|POLO_Suite|POLO_City|POLO_State|POLO_Zip|POLO_plus4|Year_in_Practice|Person_Type|Office_Phone|Exclude_flag|group_practice_id|Preferred_Email|Secondary_Email|Cell_Phone|Fax\r\nY|Cornelius           |L                   |Mayfield                      |MD|02701940604|M|1968|020|050|HPP|IM |US |N|N|N|N|                                        |PO Box 42                               |                                        |Grenada                     |MS|38902     |0042|                                        |9032 Perkins Rd                         |                                        |Baton Rouge                 |LA|70810     |1507|0|P|5135695200|N||corneliusmayfield@att.net|||2252144303\r\n\x94\x86\x94\x8cz/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/ListOfLists_1/AMA List of Lists_20230317.csv\x94C\x95\xef\xbb\xbfLIST NUMBER,CHANGED STATUS,STATUS,LIST SOURCE KEY,LIST NAME,SOURCE\r\n1,6/5/2021,REUSE,PBD,PBD Customers,Humach Files/PBD Fulfillment System Daily\r\n\x94\x86\x94\x8cu/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/FlatFile_1/SFMC_FlatFile_2023-03-16.txt\x94B\xa0\x08\x00\x00RECSEQ\tEMPPID\tBUSPID\tNAME\tBUSTITLE\tBUSNAME\tADDR1\tADDR2\tADDR3\tCITY\tSTATE\tZIP\tCOUNTRY\tDPCCODE\tDPCCHECK\tCARRTE\tLISTKEY\tGENDER\tSUP_DMACHOICE\tSUP_DM_REGION\tSUP_DNMFLAG\tSUP_DNRFLAG\tSUP_DNCFLAG\tSUP_DNEFLAG\tSOURCE_ORD\tTITLE_DESC\tPREFIX_DESC\tDAY_PHONE\tEVENING_PHONE\tFAX_NUMBER\tBEST_EMAIL\tEMAIL_MORA\tINDUSTRY_DESC\tSUP_DM\tSUP_TM\tSUP_EM\tPHYSICIANFLAG\tMEMBERFLAG\tAIMS_PRIMSPC\tAIMS_SECSPC\tALL_CHANTYPE\tALL_LASTODATE\tALL_ORIGODATE\tALL_RECNCYMOS\tALL_RECNCYGR\tALL_OORDMOS\tALL_OORDGR\tALL_FREQNOORD\tALL_FREQORDGR\tALL_DOLTOT\tALL_DOLTOTGR\tALL_DOLAVG\tALL_DOLAVGR\tALL_MAXORDOL\tALL_ORIGODOL\tALL_ORIGODOLG\tALL_ORIGCHAN\tALL_LASTCHAN\tGEN_SCORE\tGEN_DECILE\tTS_SCORE\tTS_DECILE\tTS_SEGMENT\tTS_RECENCY\tTS_FREQUENCY\tTS_TOTAL_AMT\tTS_AVG_ORDER\tTS_MAX_ORDER\tALL_LASTODOL\tALL_LASTODOLG\tCPTA_FREQ\tCPTA_RECENCY\tCPTA_ENDDATE\tCPTA_LASTSLEN\tCPTA_TOTDOL\tCPTA_AVGDOL\tCPTA_LSKUDESC\tCPTA_MAXORDOL\tONLSUB_LNOLIC\tONLSUB_SLDATE\tONLSUB_ELDATE\tONLSUB_LSTREC\tONLSUB_FREQ\tONLSUB_TOTDOL\tONLSUB_AVGDOL\tALL_PROMOFREQ\tALL_MKTDR_BIL\tALL_MKTDR_CD\tALL_MKTDR_DOC\tALL_MKTDR_PRA\tALL_MKTDR_IMP\tALL_MKTDR_TRA\tALL_FTYP_SUB\tALL_FTYP_PRNT\tALL_FTYP_DIG\tALL_FTYP_PRDG\tALL_FTYP_DATA\tALL_FTYP_BNDL\tALL_FTYP_LSUB\tALL_FTYP_LPRT\tALL_FTYP_LDIG\tALL_FTYP_LPRD\tALL_FTYP_LDTA\tALL_FTYP_LBND\tALL_FTYP_FRQ\tALL_BUYR_TYPE\tOLSUB_DSPNAME\tALL_LPROD_1\tALL_LPROD_2\tALL_FRQPROD_1\tALL_FRQPROD_2\tALL_TOT_OPEN\tALL_TOT_CLICK\tALL_TOT_BOUNC\tALL_TOT_UNSBS\tALL_TOT_SENDS\tALL_OPEN_RATE\tALL_CLCK_RATE\tALL_EMLSOPR_1\tALL_EMFROPR_1\tALL_EMLSOPR_2\tALL_EMFROPR_2\tALL_MKDR_LSCH\tALL_MKDR_FRCH\tALL_MKDR_LSTA\tALL_MKDR_FRTA\tALL_PRIMO_LST\tALL_PRIMO_FRQ\tALL_DSCAT_LST\tALL_DSCAT_FRQ\tALL_AUDNC_LST\tALL_AUDNC_FRQ\tOLSUB_AUTOREN\tALL_MK_DRV_DM\tALL_MK_DRV_CT\tALL_MK_DRV_WB\tALL_MK_DRV_TS\tALL_MK_DRVUSC\tALL_MK_DRV_EM\tALL_MK_DRV_LE\tALL_MK_DRV_FX\tALL_MK_DRV_SC\tALL_RESLLR_PR\tALL_RESLLR_AC\tALL_EVNT_LEAD\tALL_SF_LEAD\tALL_SKU_ORIG\tALL_SKU_LAST\tALL_SKU_FRQ\tEM_LASTODATE\tEM_ORIGODATE\tALL_PROD1\tALL_PROD2\tALL_ORG_PROD1\tALL_ORG_PROD2\tINDUSTRY_DESC.1\tEMAIL.1\tDAY_PHONE.1\tEVENING_PHONE.1\n0000000001\t34795\t0000034795\t\tTITLE\t\tWORK ADDR 1\tWORK ADDR 2\t\tWORK CITY WORK STATE CODE WO\t\t\t\t\t\t\tX27#\tU\t\t\tY\tY\t\t\t\t\t\t\t\t\t\t\t\tY\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tNone\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tN\tN\tN\tN\t\t\t\t\t\t\t\t\t\t\t\t\t\n\x94\x86\x94e.']


@pytest.fixture
def empty_pickled_data():
    return []
