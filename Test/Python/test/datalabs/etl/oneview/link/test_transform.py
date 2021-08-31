""" source: datalabs.etl.oneview.transform """
import logging
import pytest
import io
import pandas as pd

from   datalabs.etl.oneview.link.transform import CorporateParentBusinessTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_linking_corporate_parent_business(components):
    transformer = CorporateParentBusinessTransformerTask(components)
    csv_list = transformer._transform()
    dataframe = pd.read_csv(io.StringIO(csv_list[0].decode()))

    assert len(csv_list) == 1
    assert dataframe.columns[0] == 'child'
    assert dataframe.columns[1] == 'parent'
    assert dataframe.iloc[0]["child"] == "INS00000048"
    assert dataframe.iloc[0]["parent"] == "INS00000222"



# pylint: disable=redefined-outer-name
@pytest.fixture
def components(data):
    return dict(
        CLASS='datalabs.etl.oneview.ppd.transform.PPDTransformerTask',
        thing=True,
        data=data
    )


@pytest.fixture
def data():
    data = ',IMS_ORG_ID,BUSINESS_NAME,DBA_NAME,CARE_OF_LOCATION,ADDRESS_ID,STF_ID,PHYSICAL_ADDR_1,PHYSICAL_ADDR_2,PHYSICAL_CITY,PHYSICAL_STATE,PHYSICAL_ZIP,POSTAL_ADDR_1,POSTAL_ADDR_2,POSTAL_CITY,POSTAL_STATE,POSTAL_ZIP,PHONE,FAX,WEBSITE,LATITUDE,LONGITUDE,OWNER_STATUS,PROFIT_STATUS,CMI,PRIMARY_COT_ID,COT_CLASSIFICATION_ID,COT_CLASSIFICATION,COT_FACILITY_TYPE_ID,COT_FACILITY_TYPE,COT_SPECIALTY_ID,COT_SPECIALTY,RECORD_TYPE,BED_CLUSTER_ID,TTL_LICENSE_BEDS,TTL_CENSUS_BEDS,TTL_STAFFED_BEDS,TEACHING_HOSP,COMMHOSP,ALL_DDD,ALL_NPI,HIN,DEA,MPN,MPN_ORDER,MSA,FIPS_STATE,FIPS_COUNTY,NUM_OF_PROVIDERS,CORP_PARENT_IMS_ORG_ID,CORP_PARENT_NAME,OWNER_SUB_IMS_ORG_ID,OWNER_SUB_NAME,GPO_PHARMA_IMS_ORG_ID,GPO_PHARMA_NAME,GPO_MEDSURG_IMS_ORG_ID,GPO_MEDSURG_NAME,PHARMA_PROV_IMS_ORG_ID,PHARMA_PROV_NAME,FORMULARY,ELECTRONIC_MED_REC,EPRESCRIBE,PAYPERFORM,GENFIRST,SREP_ACCESS,DEACTIVATION_REASON,REFERBACK_IMS_ORG_ID,STATUS_INDICATOR,JOB_ID,CURRENT_BATCH_FLAG,BATCH_BUSINESS_DATE\n \
            0,INS00000004,INTALERE,,,11381522,2507581,2 CITYPLACE DR,STE 400,SAINT LOUIS,MO,63141-7096     ,2 CITYPLACE DR,STE 400,SAINT LOUIS,MO,63141-7096     ,3145421974,3145421999,intalere.com,38.672959,-90.44177,,For Profit,1.5023,5,10,Buying Organization,13,Group Purchasing Organization (GPO),,,1,,44069,28647,39992,,,,,,,,,41180,29,189,28212,,,,,,,,,,,,,,,,,,,A,64202,Y ,4/5/2019\n \
            1,INS00000048,ABINGTON HEALTH,,,24493,24493,1200 OLD YORK RD,,ABINGTON,PA,19001-3720     ,1200 OLD YORK RD,,ABINGTON,PA,19001-3720     ,2154812000,2154814014,www.amh.org,40.118959,-75.11939,,Not for Profit,1.4294,235,25,Corporate Parent,81,Owner Subsidiary,,,2,,146,73,76,,,,,,,,,37980,42,91,667,INS00000222,JEFFERSON HEALTH,,,INS00000040,"PREMIER, INC",INS00000040,"PREMIER, INC",,,Yes - Closed,Yes                 ,Yes                 ,Yes                 ,Yes                 ,Yes                 ,,,A,64202,Y ,4/5/2019\n \
            2,INS00000065,ANCILLA SYSTEMS,,,286140,286140,1000 S LAKE PARK AVE,,HOBART,IN,46342-5958     ,1000 S LAKE PARK AVE,,HOBART,IN,46342-5958     ,2199478500,2199474149,www.ancilla.org,41.522316,-87.25938,,Not for Profit,,16,25,Corporate Parent,14,Integrated Delivery Network (IDN),,,2,,,,,,,,,,,,,16980,18,89,,,,,,,,,,,,,,,,,,Facility Closed,,D,64202,Y ,4/5/2019\n \
            3,INS00000202,HENRY FORD HEALTH SYSTEM,,,6912860,6912860,1 FORD PL,,DETROIT,MI,48202-3450     ,1 FORD PL,,DETROIT,MI,48202-3450     ,3139162600,3138769243,www.henryford.com,42.363799,-83.07645,,Not for Profit,1.7722,16,25,Corporate Parent,14,Integrated Delivery Network (IDN),,,2,,2416,1771,2363,,,,,,,,,19820,26,163,4655,,,,,INS00000040,"PREMIER, INC",INS00000040,"PREMIER, INC",,,Yes - Closed,Yes                 ,Yes                 ,Yes                 ,Yes                 ,,,,A,64202,Y ,4/5/2019\n '.encode()

    return [data]
