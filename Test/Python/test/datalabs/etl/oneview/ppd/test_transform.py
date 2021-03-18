""" source: datalabs.etl.oneview.transform """
import logging
import pytest

from   datalabs.etl.oneview.ppd.transform import PPDTransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.skip(reason="Integration test. Input Credentials")
def test_jdbc_connection(components):
    transformer = PPDTransformerTask(components)
    csv_list = transformer._transform()

    assert len(csv_list) == 1
    assert csv_list[0].split(',')[0] == 'medical_education_number'


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
    data = ',ME_NUMBER,RECORD_ID,UPDATE_TYPE,ADDRESS_TYPE,MAILING_NAME,LAST_NAME,FIRST_NAME,MIDDLE_NAME,SUFFIX_CODE,' \
           'PREFERRED_ADDR2,PREFERRED_ADDR1,PREFERRED_CITY,PREFERRED_STATE,PREFERRED_ZIP,PREFERRED_PLUS4,' \
           'PREFERRED_CARRIERROUTE,UNDELIVER_FLAG,FIPS_COUNTY,FIPS_STATE,PRINTER_CONTROLCODE_BEGIN,BARCODE_ZIP,' \
           'BARCODE_PLUS4,DELIVERYPOINTCODE,CHECKDIGIT,PRINTER_CONTROLCODE_END,REGION,DIVISION,GROUP,TRACT,SUFFIX,' \
           'BLOCKGROUP,MSA_POPULATION,MICRO_METRO_IND,CBSA,CBSA_DIVISION,DEGREE_TYPE,BIRTH_YEAR,BIRTH_CITY,BIRTH_STATE,' \
           'BIRTH_COUNTRY,GENDER,PREFERREDPHONENUMBER,PENDINGDEAD_IND,FAXNUMBER,TOPCODE,PECODE,PRIMSPECIALTY,' \
           'SECONDARYSPECIALTY,MPACODE,PRAAWARDRECIPIENT,PRAEXPIRATIONDATE,GMECONFIRMFLAG,FROMDATE,ENDDATE,' \
           'YEARINPROGRAM,POSTGRADYEAR,GMEPRIMSPECIALTY,GMESECSPECIALTY,TRAINING_TYPE,GMEHOSPITALSTATE,GMEHOSPITALID,' \
           'GRADSCHOOLSTATE,GRADSCHOOLCODE,GRADYEAR,NOCONTACT_IND,NOWEBIND,PDRP_FLAG,PDRP_DATE,POLO_ADDR2,POLO_ADDR1,' \
           'POLO_CITY,POLO_STATE,POLO_ZIP,POLO_PLUS4,POLOCARRIERROUTE,MOSTRECENTFORMERLASTNAME,' \
           'MOSTRECENTFORMERMIDDLENAME,MOSTRECENTFORMERFIRSTNAME,NEXTMOSTRECENTFORMERLASTNAME,' \
           'NEXTMOSTRECENTFORMERMIDDLENAME,NEXTMOSTRECENTFORMERFIRSTNAME,JOB_ID,CURRENT_BATCH_FLAG,' \
           'BATCH_BUSINESS_DATE\r\n0,03503191317,A,1,2,MOHSIN E JAWED MD,JAWED,MOHSIN,ELAHI,,,98 ROXITICUS RD,' \
           'FAR HILLS,NJ,07931,2222,R015 ,,035,34,!,07931,2222,98,5,!,1,2,6,0458,04,3,A,1,35620,1,1,1994,NORWALK,CT,' \
           'US1,1,,,,012,050,GS ,US ,HPR,,,Y,07012019,06302024,0 ,0 ,GS ,US ,1,35,0267,035,03,2019,,,,,,,,,,,,,,,,,,' \
           ',,\r\n1,03503191333,A,1,2,FATIMA I HOSAIN MD,HOSAIN,FATIMA,IQBAL,,,13 SPY GLASS HL,HOPEWELL JCT,NY,12533,' \
           '6273,R011 ,,027,36,!,12533,6273,13,4,!,1,2,6,0501,04,2,A,1,39100,,1,1993,QUEENS,NY,US1,2,,,,012,050,EM ,' \
           'US ,HPR,,,Y,07012019,06302023,0 ,0 ,EM ,US ,1,08,0433,035,03,2019,,,,,,20 YORK ST,NEW HAVEN,CT,06510,' \
           '3220,C098 ,,,,,,,,,\r\n2,03503191341,A,1,2,MEAGHAN FLATLEY MD,FLATLEY,MEAGHAN,,,,223 BRACKENRIDGE AVE APT' \
           ' 8410,SAN ANTONIO,TX,78209,7065,C011 ,,029,48,!,78209,7065,10,5,!,3,7,6,1920,00,2,A,1,41700,,1,1993,' \
           'MINEOLA,,US1,2,,,,012,050,US ,US ,HPR,,,,,,,,,,,,,035,03,2019,,,,,,3551 ROGER BROOKE DR,JBSA FSH,TX,' \
           '78234,4504,C054 ,,,,,,,,,\r\n3,03503191350,A,1,2,JAIMIE M PARAMBIL MD,PARAMBIL,JAIMIE,MARY,,,15 ' \
           'WOODLANDS AVE N,WHITE PLAINS,NY,10607,2510,C019 ,,119,36,!,10607,2510,15,2,!,1,2,6,0111,01,4,A,1,35620,' \
           '1,1,1993,BRONX,,US1,2,,,,012,050,US ,US ,HPR,,,,,,,,,,,,,035,03,2020,,,,,,,,,,,,,,,,,,,,\r\n4,' \
           '03503191368,A,1,2,TIMOTHY HARTIGAN MD,HARTIGAN,TIMOTHY,,,,6410 LAKEMONT CT,EAST AMHERST,NY,14051,2069,' \
           'R010 ,,029,36,!,14051,2069,10,1,!,1,2,6,0146,04,1,A,1,15380,,1,1993,BUFFALO,NY,US1,1,,,,012,050,MPD,US ,' \
           'HPR,,,Y,07012019,06302023,0 ,0 ,MPD,US ,1,35,0345,035,03,2019,,,,,,,,,,,,,,,,,,,,\r\n'

    return [data]
