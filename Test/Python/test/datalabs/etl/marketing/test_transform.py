""" source: datalabs.etl.marketing.aggregate.transform """
import pickle

import pandas as pd
import pytest


from   datalabs.etl.marketing.aggregate.column import ADHOC_COLUMNS,AIMS_COLUMNS,LIST_OF_LISTS_COLUMNS
from   datalabs.etl.marketing.aggregate.transform import InputDataCleanerTask, InputsMergerTask, FlatfileUpdaterTask


# pylint: disable=redefined-outer-name
def test_input_data_cleaner_transformer_extract_all_files(pickled_data):
    named_files_data = load_tuple_data(pickled_data)

    named_files_list = [
        '2023ViVESpeakers_03142023.csv',
        'CPT Dev Program Sign Ups Since 021022_20230316.csv',
        'CPT Intl _CU_INTL.csv',
        'mbr_info_20230101.dat',
        'AMA List of Lists_20230317.csv',
        'SFMC_FlatFile_2023-03-16.txt'
    ]

    for index, named_file in enumerate(named_files_data):
        assert (named_files_list[index] in named_file[0]) is True

        assert len(named_files_data) == 6


# pylint: disable=redefined-outer-name, protected-access
def test_input_data_cleaner_transformer_merge_adhoc_data(pickled_data):
    transformer = InputDataCleanerTask({}, pickled_data)
    named_files_data = load_tuple_data(pickled_data)

    input_adhoc_files = transformer._merge_adhoc_data(named_files_data)

    assert isinstance(input_adhoc_files, pd.DataFrame)
    assert input_adhoc_files.shape[0] == 3
    assert input_adhoc_files.shape[1] == 16


# pylint: disable=redefined-outer-name, protected-access
def test_input_data_cleaner_transformer_read_input_data(pickled_data):
    read_input_files = read_input_data(pickled_data)

    assert isinstance(read_input_files.adhoc, pd.DataFrame)
    assert isinstance(read_input_files.aims, pd.DataFrame)
    assert isinstance(read_input_files.list_of_lists, pd.DataFrame)
    assert isinstance(read_input_files.flatfile, pd.DataFrame)


# pylint: disable=redefined-outer-name, protected-access
def test_input_data_cleaner_transformer_clean_input_data(pickled_data):
    transformer = InputDataCleanerTask({}, pickled_data)

    input_data = read_input_data(pickled_data)
    clean_input_files = transformer._clean_input_data(input_data)

    assert list(clean_input_files.adhoc.columns) == list(ADHOC_COLUMNS.values())
    assert list(clean_input_files.aims.columns) == list(AIMS_COLUMNS.values()) + ["PHYSICIANFLAG"]
    assert list(clean_input_files.list_of_lists.columns) == list(LIST_OF_LISTS_COLUMNS.values())


# pylint: disable=redefined-outer-name, protected-access
def test_input_data_cleaner_transformer_output_data(pickled_data):
    transformer = InputDataCleanerTask({},pickled_data)
    output_files = transformer.run()

    assert len(output_files) == 4


# pylint: disable=redefined-outer-name, protected-access
def test_empty_input_data_cleaner_transformer(empty_pickled_data):
    transformer = InputDataCleanerTask({}, empty_pickled_data)

    with pytest.raises(IndexError) as exception:
        transformer.run()

    assert exception.value.args[0] == 'list index out of range'


# pylint: disable=redefined-outer-name, protected-access
def test_input_merger_transformer_merge_input_data(input_merger_data):
    transformer = InputsMergerTask({}, input_merger_data)

    input_data = read_input_merger_data(input_merger_data)

    merged_inputs = transformer._merge_input_data(input_data)

    assert merged_inputs.shape[0] == 3
    assert merged_inputs.shape[1] == 23


# pylint: disable=redefined-outer-name, protected-access
def test_empty_input_merger_transformer(empty_pickled_data):
    transformer = InputDataCleanerTask({}, empty_pickled_data)

    with pytest.raises(IndexError) as exception:
        transformer.run()

    assert exception.value.args[0] == 'list index out of range'


def test_flatfileupdater_read_datasets(flatfileupdater_transformer, flatfileupdater_data):
    inputs = flatfileupdater_transformer._read_input_data(flatfileupdater_data)
    assert len(inputs) == 4

    return inputs


# pylint: disable=redefined-outer-name, protected-access
def test_flatfile_updater_prune_flatfile_listkeys(flatfileupdater_transformer, flatfileupdater_data):
    contacts, list_of_lists, flatfile, inputs = test_flatfileupdater_read_datasets(
                                                    flatfileupdater_transformer,
                                                    flatfileupdater_data
                                                )
    flatfile = flatfileupdater_transformer._prune_flatfile_listkeys(flatfile, list_of_lists)

    assert len(flatfile) == 6
    assert flatfile.LISTKEY[0] == 'X32#Z19#Z19#'
    assert flatfile.LISTKEY[2] == 'WBR#X27#'
    assert flatfile.LISTKEY[4] == ''

    return [contacts, list_of_lists, flatfile, inputs]


# pylint: disable=redefined-outer-name, protected-access
def test_flatfile_updater_assign_emppids_to_inputs(flatfileupdater_transformer, flatfileupdater_data):
    contacts, _, flatfile, inputs = test_flatfile_updater_prune_flatfile_listkeys(
                                        flatfileupdater_transformer, flatfileupdater_data
                                    )

    matched_inputs, unmatched_inputs = flatfileupdater_transformer._assign_emppids_to_inputs(inputs, flatfile)
    unmatched_inputs = unmatched_inputs.reset_index()

    assert len(unmatched_inputs) == 2
    assert unmatched_inputs.BEST_EMAIL[0] == 'dweepkumar@outlook.com'
    assert unmatched_inputs.BEST_EMAIL[1] == 'mt.michicainternational@gmail.com'

    return [contacts, flatfile, matched_inputs, unmatched_inputs]

# pylint: disable=redefined-outer-name, protected-access
def test_flatfile_updater_add_new_records_to_flatfile(flatfileupdater_transformer, flatfileupdater_data):
    contacts, flatfile, matched_inputs, unmatched_inputs = test_flatfile_updater_assign_emppids_to_inputs(
                                                               flatfileupdater_transformer,
                                                               flatfileupdater_data
                                                           )
    assert len(flatfile) == 6

    flatfile = flatfileupdater_transformer._add_new_records_to_flatfile(flatfile, unmatched_inputs)

    assert len(flatfile) == 8
    return [contacts, flatfile, matched_inputs, unmatched_inputs]


def test_flatfile_updater_update_flatfile_listkeys(flatfileupdater_transformer, flatfileupdater_data):
    contacts, flatfile, matched_inputs, _ = test_flatfile_updater_add_new_records_to_flatfile(
                                                flatfileupdater_transformer,
                                                flatfileupdater_data
                                            )

    assert flatfile.LISTKEY[0] == 'X32#Z19#Z19#'
    assert flatfile.LISTKEY[1] == 'X27#'
    assert flatfile.LISTKEY[2] == 'WBR#X27#'

    flatfile = flatfileupdater_transformer._update_flatfile_listkeys(flatfile, matched_inputs)

    assert flatfile.LISTKEY[0] == 'X32#Z19#Z19#ATG#'
    assert flatfile.LISTKEY[1] == 'X27#ATG#PBD#X27#'
    assert flatfile.LISTKEY[2] == 'WBR#X27#Z29#'

    assert len(flatfile) == 8

    return [contacts, flatfile]


def test_flatfile_updater_assign_new_contact_ids_to_flatfile(flatfileupdater_transformer, flatfileupdater_data):
    contacts, flatfile = test_flatfile_updater_update_flatfile_listkeys(
                             flatfileupdater_transformer,
                             flatfileupdater_data
                         )

    assert len([x for x in flatfile.hs_contact_id if x !='']) == 6

    flatfile = flatfileupdater_transformer._assign_new_contact_ids_to_flatfile(flatfile, contacts)
    assert len(list(flatfile.hs_contact_id)) == 8


def load_tuple_data(pickled_data):
    named_files_data = pickle.loads(pickled_data[0])

    return named_files_data


def read_input_data(pickled_data):
    transformer = InputDataCleanerTask({}, pickled_data)
    named_files_data = load_tuple_data(pickled_data)
    read_input_files = transformer._read_input_data(named_files_data)

    return read_input_files


def read_input_merger_data(input_merger_data):
    transformer = InputsMergerTask({}, input_merger_data)
    read_input_files = transformer._read_input_data(input_merger_data)

    return read_input_files


# pylint: disable=line-too-long
@pytest.fixture
def pickled_data():
    return [b'\x80\x04\x95\xf0\x12\x00\x00\x00\x00\x00\x00]\x94(\x8cs/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/Adhoc_1/2023ViVESpeakers_03142023.csv\x94B\x1a\x01\x00\x00\xef\xbb\xbfCUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC,File_Name\r\n,Abby Levy,Managing Partner,Primetime Partners,13310 Rhodine Rd,,,Riverview,FL,33579,United States,abby@primetimepartners.com,,,2023 ViVE Speakers,\r\n\x94\x86\x94\x8c\x88/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/Adhoc_1/CPT Dev Program Sign Ups Since 021022_20230316.csv\x94C\xb5\xef\xbb\xbfCUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC,File_Name\r\n97, ,,,,,,,,,,drs26@cornell.edu,,,Health-tech,\r\n\x94\x86\x94\x8ck/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/Adhoc_1/CPT Intl _CU_INTL.csv\x94B\x05\x01\x00\x00\xef\xbb\xbfCUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC,File_Name\r\n,Tathagata Ray,"Manager, Business Intelligence",Sonic Incytes Medical Corp,,,,,,,Canada,tathagata@sonicincytes.com,,,CPT Intl,\r\n\x94\x86\x94\x8cj/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/AIMS_1/mbr_info_20230101.dat\x94B\xe7\x03\x00\x00#AMA_Membership_Flag|First_Name|Middle_Name|Last_Name|Degree_Type|ME_Nbr|Gender|Birth_Yr|TOP|PE_Code|MPA_Code|Prim_Spec_Cd|Sec_Spec_Cd|No_Contact_Flag|Do_no_rent_flag|do_not_solicit|Do_not_mail/email_flag|PPMA_Addr1|PPMA_Addr2|PPMA_Suite|PPMA_City|PPMA_State|PPMA_Zip|PPMA_plus4|POLO_Addr1|POLO_Addr2|POLO_Suite|POLO_City|POLO_State|POLO_Zip|POLO_plus4|Year_in_Practice|Person_Type|Office_Phone|Exclude_flag|group_practice_id|Preferred_Email|Secondary_Email|Cell_Phone|Fax\r\nY|Cornelius           |L                   |Mayfield                      |MD|02701940604|M|1968|020|050|HPP|IM |US |N|N|N|N|                                        |PO Box 42                               |                                        |Grenada                     |MS|38902     |0042|                                        |9032 Perkins Rd                         |                                        |Baton Rouge                 |LA|70810     |1507|0|P|5135695200|N||corneliusmayfield@att.net|||2252144303\r\n\x94\x86\x94\x8cz/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/ListOfLists_1/AMA List of Lists_20230317.csv\x94C\x95\xef\xbb\xbfLIST NUMBER,CHANGED STATUS,STATUS,LIST SOURCE KEY,LIST NAME,SOURCE\r\n1,6/5/2021,REUSE,PBD,PBD Customers,Humach Files/PBD Fulfillment System Daily\r\n\x94\x86\x94\x8cu/mnt/c/Users/rsun/OneDrive - American Medical Association/data/cpt/files/load/FlatFile_1/SFMC_FlatFile_2023-03-16.txt\x94B\xa0\x08\x00\x00RECSEQ\tEMPPID\tBUSPID\tNAME\tBUSTITLE\tBUSNAME\tADDR1\tADDR2\tADDR3\tCITY\tSTATE\tZIP\tCOUNTRY\tDPCCODE\tDPCCHECK\tCARRTE\tLISTKEY\tGENDER\tSUP_DMACHOICE\tSUP_DM_REGION\tSUP_DNMFLAG\tSUP_DNRFLAG\tSUP_DNCFLAG\tSUP_DNEFLAG\tSOURCE_ORD\tTITLE_DESC\tPREFIX_DESC\tDAY_PHONE\tEVENING_PHONE\tFAX_NUMBER\tBEST_EMAIL\tEMAIL_MORA\tINDUSTRY_DESC\tSUP_DM\tSUP_TM\tSUP_EM\tPHYSICIANFLAG\tMEMBERFLAG\tAIMS_PRIMSPC\tAIMS_SECSPC\tALL_CHANTYPE\tALL_LASTODATE\tALL_ORIGODATE\tALL_RECNCYMOS\tALL_RECNCYGR\tALL_OORDMOS\tALL_OORDGR\tALL_FREQNOORD\tALL_FREQORDGR\tALL_DOLTOT\tALL_DOLTOTGR\tALL_DOLAVG\tALL_DOLAVGR\tALL_MAXORDOL\tALL_ORIGODOL\tALL_ORIGODOLG\tALL_ORIGCHAN\tALL_LASTCHAN\tGEN_SCORE\tGEN_DECILE\tTS_SCORE\tTS_DECILE\tTS_SEGMENT\tTS_RECENCY\tTS_FREQUENCY\tTS_TOTAL_AMT\tTS_AVG_ORDER\tTS_MAX_ORDER\tALL_LASTODOL\tALL_LASTODOLG\tCPTA_FREQ\tCPTA_RECENCY\tCPTA_ENDDATE\tCPTA_LASTSLEN\tCPTA_TOTDOL\tCPTA_AVGDOL\tCPTA_LSKUDESC\tCPTA_MAXORDOL\tONLSUB_LNOLIC\tONLSUB_SLDATE\tONLSUB_ELDATE\tONLSUB_LSTREC\tONLSUB_FREQ\tONLSUB_TOTDOL\tONLSUB_AVGDOL\tALL_PROMOFREQ\tALL_MKTDR_BIL\tALL_MKTDR_CD\tALL_MKTDR_DOC\tALL_MKTDR_PRA\tALL_MKTDR_IMP\tALL_MKTDR_TRA\tALL_FTYP_SUB\tALL_FTYP_PRNT\tALL_FTYP_DIG\tALL_FTYP_PRDG\tALL_FTYP_DATA\tALL_FTYP_BNDL\tALL_FTYP_LSUB\tALL_FTYP_LPRT\tALL_FTYP_LDIG\tALL_FTYP_LPRD\tALL_FTYP_LDTA\tALL_FTYP_LBND\tALL_FTYP_FRQ\tALL_BUYR_TYPE\tOLSUB_DSPNAME\tALL_LPROD_1\tALL_LPROD_2\tALL_FRQPROD_1\tALL_FRQPROD_2\tALL_TOT_OPEN\tALL_TOT_CLICK\tALL_TOT_BOUNC\tALL_TOT_UNSBS\tALL_TOT_SENDS\tALL_OPEN_RATE\tALL_CLCK_RATE\tALL_EMLSOPR_1\tALL_EMFROPR_1\tALL_EMLSOPR_2\tALL_EMFROPR_2\tALL_MKDR_LSCH\tALL_MKDR_FRCH\tALL_MKDR_LSTA\tALL_MKDR_FRTA\tALL_PRIMO_LST\tALL_PRIMO_FRQ\tALL_DSCAT_LST\tALL_DSCAT_FRQ\tALL_AUDNC_LST\tALL_AUDNC_FRQ\tOLSUB_AUTOREN\tALL_MK_DRV_DM\tALL_MK_DRV_CT\tALL_MK_DRV_WB\tALL_MK_DRV_TS\tALL_MK_DRVUSC\tALL_MK_DRV_EM\tALL_MK_DRV_LE\tALL_MK_DRV_FX\tALL_MK_DRV_SC\tALL_RESLLR_PR\tALL_RESLLR_AC\tALL_EVNT_LEAD\tALL_SF_LEAD\tALL_SKU_ORIG\tALL_SKU_LAST\tALL_SKU_FRQ\tEM_LASTODATE\tEM_ORIGODATE\tALL_PROD1\tALL_PROD2\tALL_ORG_PROD1\tALL_ORG_PROD2\tINDUSTRY_DESC.1\tEMAIL.1\tDAY_PHONE.1\tEVENING_PHONE.1\n0000000001\t34795\t0000034795\t\tTITLE\t\tWORK ADDR 1\tWORK ADDR 2\t\tWORK CITY WORK STATE CODE WO\t\t\t\t\t\t\tX27#\tU\t\t\tY\tY\t\t\t\t\t\t\t\t\t\t\t\tY\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tNone\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tN\tN\tN\tN\t\t\t\t\t\t\t\t\t\t\t\t\t\n\x94\x86\x94e.']

@pytest.fixture
def empty_pickled_data():
    return []


# pylint: disable=line-too-long
@pytest.fixture
def input_merger_data():
    return [b'CUSTOMER_ID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,BEST_EMAIL,DAY_PHONE,EVENING_PHONE,INDUSTRY_DESC,File_Name\r\n,Abby Levy,Managing Partner,Primetime Partners,13310 Rhodine Rd,,,Riverview,FL,33579,United States,abby@primetimepartners.com,,,2023 ViVE Speakers,PBD Customers\r\n97, ,,,,,,,,,,drs26@cornell.edu,,,Health-tech,PBD Customers\r\n,Tathagata Ray,"Manager, Business Intelligence",Sonic Incytes Medical Corp,,,,,,,Canada,tathagata@sonicincytes.com,,,CPT Intl,PBD Customers\r\n', b'MEMBERFLAG,ME_Nbr,GENDER,AIMS_PRIMSPC,AIMS_SECSPC,SUP_DNRFLAG,SUP_DNMFLAG,BEST_EMAIL,PHYSICIANFLAG\r\nY,2701940604,M,IM ,US ,N,N,abby@primetimepartners.com,Y\r\n', b'LIST NUMBER,CHANGED STATUS,STATUS,LISTKEY,LIST NAME,SOURCE\n1,6/5/2021,REUSE,PBD#,PBD Customers,Humach Files/PBD Fulfillment System Daily\n', b'RECSEQ,EMPPID,BUSPID,NAME,BUSTITLE,BUSNAME,ADDR1,ADDR2,ADDR3,CITY,STATE,ZIP,COUNTRY,DPCCODE,DPCCHECK,CARRTE,LISTKEY,GENDER,SUP_DMACHOICE,SUP_DM_REGION,SUP_DNMFLAG,SUP_DNRFLAG,SUP_DNCFLAG,SUP_DNEFLAG,SOURCE_ORD,TITLE_DESC,PREFIX_DESC,DAY_PHONE,EVENING_PHONE,FAX_NUMBER,BEST_EMAIL,EMAIL_MORA,INDUSTRY_DESC,SUP_DM,SUP_TM,SUP_EM,PHYSICIANFLAG,MEMBERFLAG,AIMS_PRIMSPC,AIMS_SECSPC,ALL_CHANTYPE,ALL_LASTODATE,ALL_ORIGODATE,ALL_RECNCYMOS,ALL_RECNCYGR,ALL_OORDMOS,ALL_OORDGR,ALL_FREQNOORD,ALL_FREQORDGR,ALL_DOLTOT,ALL_DOLTOTGR,ALL_DOLAVG,ALL_DOLAVGR,ALL_MAXORDOL,ALL_ORIGODOL,ALL_ORIGODOLG,ALL_ORIGCHAN,ALL_LASTCHAN,GEN_SCORE,GEN_DECILE,TS_SCORE,TS_DECILE,TS_SEGMENT,TS_RECENCY,TS_FREQUENCY,TS_TOTAL_AMT,TS_AVG_ORDER,TS_MAX_ORDER,ALL_LASTODOL,ALL_LASTODOLG,CPTA_FREQ,CPTA_RECENCY,CPTA_ENDDATE,CPTA_LASTSLEN,CPTA_TOTDOL,CPTA_AVGDOL,CPTA_LSKUDESC,CPTA_MAXORDOL,ONLSUB_LNOLIC,ONLSUB_SLDATE,ONLSUB_ELDATE,ONLSUB_LSTREC,ONLSUB_FREQ,ONLSUB_TOTDOL,ONLSUB_AVGDOL,ALL_PROMOFREQ,ALL_MKTDR_BIL,ALL_MKTDR_CD,ALL_MKTDR_DOC,ALL_MKTDR_PRA,ALL_MKTDR_IMP,ALL_MKTDR_TRA,ALL_FTYP_SUB,ALL_FTYP_PRNT,ALL_FTYP_DIG,ALL_FTYP_PRDG,ALL_FTYP_DATA,ALL_FTYP_BNDL,ALL_FTYP_LSUB,ALL_FTYP_LPRT,ALL_FTYP_LDIG,ALL_FTYP_LPRD,ALL_FTYP_LDTA,ALL_FTYP_LBND,ALL_FTYP_FRQ,ALL_BUYR_TYPE,OLSUB_DSPNAME,ALL_LPROD_1,ALL_LPROD_2,ALL_FRQPROD_1,ALL_FRQPROD_2,ALL_TOT_OPEN,ALL_TOT_CLICK,ALL_TOT_BOUNC,ALL_TOT_UNSBS,ALL_TOT_SENDS,ALL_OPEN_RATE,ALL_CLCK_RATE,ALL_EMLSOPR_1,ALL_EMFROPR_1,ALL_EMLSOPR_2,ALL_EMFROPR_2,ALL_MKDR_LSCH,ALL_MKDR_FRCH,ALL_MKDR_LSTA,ALL_MKDR_FRTA,ALL_PRIMO_LST,ALL_PRIMO_FRQ,ALL_DSCAT_LST,ALL_DSCAT_FRQ,ALL_AUDNC_LST,ALL_AUDNC_FRQ,OLSUB_AUTOREN,ALL_MK_DRV_DM,ALL_MK_DRV_CT,ALL_MK_DRV_WB,ALL_MK_DRV_TS,ALL_MK_DRVUSC,ALL_MK_DRV_EM,ALL_MK_DRV_LE,ALL_MK_DRV_FX,ALL_MK_DRV_SC,ALL_RESLLR_PR,ALL_RESLLR_AC,ALL_EVNT_LEAD,ALL_SF_LEAD,ALL_SKU_ORIG,ALL_SKU_LAST,ALL_SKU_FRQ,EM_LASTODATE,EM_ORIGODATE,ALL_PROD1,ALL_PROD2,ALL_ORG_PROD1,ALL_ORG_PROD2,INDUSTRY_DESC.1,EMAIL.1,DAY_PHONE.1,EVENING_PHONE.1\n0000000001,34795,0000034795,,TITLE,,WORK ADDR 1,WORK ADDR 2,,WORK CITY WORK STATE CODE WO,,,,,,,X27#,U,,,Y,Y,,,,,,,,,,,,Y,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,None,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,N,N,N,N,,,,,,,,,,,,,\n']


@pytest.fixture
def flatfile_data():
    return b"""EMPPID,LISTKEY,BEST_EMAIL,id,hs_contact_id,email_last_validated,months_since_validated,update
34797,X32#PBD#Z19#Z19#,psurati86@gmail.com,34797,90ex1xXJjlAqyT6,1/1/2023,TRUE
35627,X27#,ahnhs@korea.ac.kr,35627,4L1gUCqG6T2JTqb,5/1/2023,TRUE
35824,PBD#WBR#X27#,jeremy@getpatch.com,35824,1PE2wj4FrGXRQc6,5/13/2023,FALSE
34799,X32#,malloryj@northernmnnetwork.org,34799,uk6ogcgsH0Qjhrh,5/23/2023,FALSE
34796,SEL#,abby@primetimepartners.com,34796,2STd4lNKbL9CzJk,8/23/2023,FALSE
35829,X27#,jeremy@getpatch.com,35824,1PE2wj4FrGXRQc6,6/13/2023,FALSE
"""


@pytest.fixture
def flatfileupdater_data(contacts_data, validated_list_of_lists_data, validated_flatfile_data, validated_inputs_data):
    return [
        contacts_data,
        validated_list_of_lists_data,
        validated_flatfile_data,
        validated_inputs_data
    ]


@pytest.fixture
def flatfileupdater_parameters(flatfileupdater_data):
    return dict(
        data=flatfileupdater_data
    )


@pytest.fixture
def contacts_data():
    return b"""id,hs_contact_id,email_last_validated
34797,90ex1xXJjlAqyT6,1/1/2023
35627,4L1gUCqG6T2JTqb,5/1/2023
35824,1PE2wj4FrGXRQc6,5/13/2023
34799,uk6ogcgsH0Qjhrh,5/23/2023
34796,2STd4lNKbL9CzJk,8/23/2023
"""


@pytest.fixture
def validated_list_of_lists_data():
    return b"""STATUS,LISTKEY,SOURCE
REPLACE,PBD#,Adhoc Files
REUSE,ATG#,PBD Fulfillment System Quarterly Winback
REUSE,WBR#,Adhoc Files
REMOVE,SEL#,ATG eCommerce/Customer Online Coding Orders Weekly
REUSE,Z29#,Humach Files/PBD Fulfillment System Daily
"""


@pytest.fixture
def validated_flatfile_data():
    return b"""EMPPID,LISTKEY,BEST_EMAIL,id,hs_contact_id,email_last_validated,months_since_validated,update
34797,X32#PBD#Z19#Z19#,psurati86@gmail.com,34797,90ex1xXJjlAqyT6,1/1/2023,TRUE
35627,X27#,ahnhs@korea.ac.kr,35627,4L1gUCqG6T2JTqb,5/1/2023,TRUE
35824,PBD#WBR#X27#,jeremy@getpatch.com,35824,1PE2wj4FrGXRQc6,5/13/2023,FALSE
34799,X32#,malloryj@northernmnnetwork.org,34799,uk6ogcgsH0Qjhrh,5/23/2023,FALSE
34796,SEL#,abby@primetimepartners.com,34796,2STd4lNKbL9CzJk,8/23/2023,FALSE
35829,X27#,jeremy@getpatch.com,35824,1PE2wj4FrGXRQc6,6/13/2023,FALSE
"""


@pytest.fixture
def validated_inputs_data():
    return b"""NAME,BEST_EMAIL,LISTKEY,LISTKEY_COMBINED,email_last_validated,months_since_validated,update
    Juan B,ahnhs@korea.ac.kr,ATG#PBD#,ATG#,3/1/2023,6,TRUE
    Peets E,psurati86@gmail.com,ATG#,X32#Z19#Z19#,1/1/2023,11,TRUE
    Juan B,ahnhs@korea.ac.kr,X27#,X27#,5/1/2023,6,TRUE
    Jimmy N,jeremy@getpatch.com,Z29#,27#,5/13/2023,0,FALSE
    Mark W,dweepkumar@outlook.com,SEL#,SEL#,5/23/2023,0,FALSE
    Abby,mt.michicainternational@gmail.com,PBD#,Z29#,8/23/2023,0,FALSE
"""


@pytest.fixture
def flatfileupdater_transformer(flatfileupdater_parameters):
    return FlatfileUpdaterTask(flatfileupdater_parameters)
