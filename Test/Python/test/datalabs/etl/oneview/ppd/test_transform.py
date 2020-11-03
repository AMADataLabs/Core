import logging
import os
import pandas
import pytest

import datalabs.etl.task as task
from   datalabs.etl.oneview.ppd.transform import PPDTransformer

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.mark.skip(reason="Integration test. Input Credentials")
def test_jdbc_connection(components):
    transformer = PPDTransformer(components)
    csv_list = transformer._transform()

    assert len(csv_list) == 1
    assert csv_list[0].split(',')[0] == 'medical_education_number'


@pytest.fixture
def components(dataframe):
    return task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='datalabs.etl.oneview.ppd.transform.PPDTransformer', thing=True),
            data=dataframe
        )


@pytest.fixture
def dataframe():
    data = {'ME_NUMBER': {0: '03503191317',
                          1: '03503191333',
                          2: '03503191341',
                          3: '03503191350',
                          4: '03503191368'},
            'RECORD_ID': {0: 'A', 1: 'A', 2: 'A', 3: 'A', 4: 'A'},
            'UPDATE_TYPE': {0: '1', 1: '1', 2: '1', 3: '1', 4: '1'},
            'ADDRESS_TYPE': {0: '2', 1: '2', 2: '2', 3: '2', 4: '2'},
            'MAILING_NAME': {0: 'MOHSIN E JAWED MD',
                             1: 'FATIMA I HOSAIN MD',
                             2: 'MEAGHAN FLATLEY MD',
                             3: 'JAIMIE M PARAMBIL MD',
                             4: 'TIMOTHY HARTIGAN MD'},
            'LAST_NAME': {0: 'JAWED',
                          1: 'HOSAIN',
                          2: 'FLATLEY',
                          3: 'PARAMBIL',
                          4: 'HARTIGAN'},
            'FIRST_NAME': {0: 'MOHSIN',
                           1: 'FATIMA',
                           2: 'MEAGHAN',
                           3: 'JAIMIE',
                           4: 'TIMOTHY'},
            'MIDDLE_NAME': {0: 'ELAHI', 1: 'IQBAL', 2: None, 3: 'MARY', 4: None},
            'SUFFIX_CODE': {0: None, 1: None, 2: None, 3: None, 4: None},
            'PREFERRED_ADDR2': {0: None, 1: None, 2: None, 3: None, 4: None},
            'PREFERRED_ADDR1': {0: '98 ROXITICUS RD',
                                1: '13 SPY GLASS HL',
                                2: '223 BRACKENRIDGE AVE APT 8410',
                                3: '15 WOODLANDS AVE N',
                                4: '6410 LAKEMONT CT'},
            'PREFERRED_CITY': {0: 'FAR HILLS',
                               1: 'HOPEWELL JCT',
                               2: 'SAN ANTONIO',
                               3: 'WHITE PLAINS',
                               4: 'EAST AMHERST'},
            'PREFERRED_STATE': {0: 'NJ', 1: 'NY', 2: 'TX', 3: 'NY', 4: 'NY'},
            'PREFERRED_ZIP': {0: '07931', 1: '12533', 2: '78209', 3: '10607', 4: '14051'},
            'PREFERRED_PLUS4': {0: '2222', 1: '6273', 2: '7065', 3: '2510', 4: '2069'},
            'PREFERRED_CARRIERROUTE': {0: 'R015 ',
                                       1: 'R011 ',
                                       2: 'C011 ',
                                       3: 'C019 ',
                                       4: 'R010 '},
            'UNDELIVER_FLAG': {0: None, 1: None, 2: None, 3: None, 4: None},
            'FIPS_COUNTY': {0: '035', 1: '027', 2: '029', 3: '119', 4: '029'},
            'FIPS_STATE': {0: '34', 1: '36', 2: '48', 3: '36', 4: '36'},
            'PRINTER_CONTROLCODE_BEGIN': {0: '!', 1: '!', 2: '!', 3: '!', 4: '!'},
            'BARCODE_ZIP': {0: '07931', 1: '12533', 2: '78209', 3: '10607', 4: '14051'},
            'BARCODE_PLUS4': {0: '2222', 1: '6273', 2: '7065', 3: '2510', 4: '2069'},
            'DELIVERYPOINTCODE': {0: '98', 1: '13', 2: '10', 3: '15', 4: '10'},
            'CHECKDIGIT': {0: '5', 1: '4', 2: '5', 3: '2', 4: '1'},
            'PRINTER_CONTROLCODE_END': {0: '!', 1: '!', 2: '!', 3: '!', 4: '!'},
            'REGION': {0: '1', 1: '1', 2: '3', 3: '1', 4: '1'},
            'DIVISION': {0: '2', 1: '2', 2: '7', 3: '2', 4: '2'},
            'GROUP': {0: '6', 1: '6', 2: '6', 3: '6', 4: '6'},
            'TRACT': {0: '0458', 1: '0501', 2: '1920', 3: '0111', 4: '0146'},
            'SUFFIX': {0: '04', 1: '04', 2: '00', 3: '01', 4: '04'},
            'BLOCKGROUP': {0: '3', 1: '2', 2: '2', 3: '4', 4: '1'},
            'MSA_POPULATION': {0: 'A', 1: 'A', 2: 'A', 3: 'A', 4: 'A'},
            'MICRO_METRO_IND': {0: '1', 1: '1', 2: '1', 3: '1', 4: '1'},
            'CBSA': {0: '35620', 1: '39100', 2: '41700', 3: '35620', 4: '15380'},
            'CBSA_DIVISION': {0: '1', 1: None, 2: None, 3: '1', 4: None},
            'DEGREE_TYPE': {0: '1', 1: '1', 2: '1', 3: '1', 4: '1'},
            'BIRTH_YEAR': {0: '1994', 1: '1993', 2: '1993', 3: '1993', 4: '1993'},
            'BIRTH_CITY': {0: 'NORWALK',
                           1: 'QUEENS',
                           2: 'MINEOLA',
                           3: 'BRONX',
                           4: 'BUFFALO'},
            'BIRTH_STATE': {0: 'CT', 1: 'NY', 2: None, 3: None, 4: 'NY'},
            'BIRTH_COUNTRY': {0: 'US1', 1: 'US1', 2: 'US1', 3: 'US1', 4: 'US1'},
            'GENDER': {0: '1', 1: '2', 2: '2', 3: '2', 4: '1'},
            'PREFERREDPHONENUMBER': {0: None, 1: None, 2: None, 3: None, 4: None},
            'PENDINGDEAD_IND': {0: None, 1: None, 2: None, 3: None, 4: None},
            'FAXNUMBER': {0: None, 1: None, 2: None, 3: None, 4: None},
            'TOPCODE': {0: '012', 1: '012', 2: '012', 3: '012', 4: '012'},
            'PECODE': {0: '050', 1: '050', 2: '050', 3: '050', 4: '050'},
            'PRIMSPECIALTY': {0: 'GS ', 1: 'EM ', 2: 'US ', 3: 'US ', 4: 'MPD'},
            'SECONDARYSPECIALTY': {0: 'US ', 1: 'US ', 2: 'US ', 3: 'US ', 4: 'US '},
            'MPACODE': {0: 'HPR', 1: 'HPR', 2: 'HPR', 3: 'HPR', 4: 'HPR'},
            'PRAAWARDRECIPIENT': {0: None, 1: None, 2: None, 3: None, 4: None},
            'PRAEXPIRATIONDATE': {0: None, 1: None, 2: None, 3: None, 4: None},
            'GMECONFIRMFLAG': {0: 'Y', 1: 'Y', 2: None, 3: None, 4: 'Y'},
            'FROMDATE': {0: '07012019', 1: '07012019', 2: None, 3: None, 4: '07012019'},
            'ENDDATE': {0: '06302024', 1: '06302023', 2: None, 3: None, 4: '06302023'},
            'YEARINPROGRAM': {0: '0 ', 1: '0 ', 2: None, 3: None, 4: '0 '},
            'POSTGRADYEAR': {0: '0 ', 1: '0 ', 2: None, 3: None, 4: '0 '},
            'GMEPRIMSPECIALTY': {0: 'GS ', 1: 'EM ', 2: None, 3: None, 4: 'MPD'},
            'GMESECSPECIALTY': {0: 'US ', 1: 'US ', 2: None, 3: None, 4: 'US '},
            'TRAINING_TYPE': {0: '1', 1: '1', 2: None, 3: None, 4: '1'},
            'GMEHOSPITALSTATE': {0: '35', 1: '08', 2: None, 3: None, 4: '35'},
            'GMEHOSPITALID': {0: '0267', 1: '0433', 2: None, 3: None, 4: '0345'},
            'GRADSCHOOLSTATE': {0: '035', 1: '035', 2: '035', 3: '035', 4: '035'},
            'GRADSCHOOLCODE': {0: '03', 1: '03', 2: '03', 3: '03', 4: '03'},
            'GRADYEAR': {0: '2019', 1: '2019', 2: '2019', 3: '2020', 4: '2019'},
            'NOCONTACT_IND': {0: None, 1: None, 2: None, 3: None, 4: None},
            'NOWEBIND': {0: None, 1: None, 2: None, 3: None, 4: None},
            'PDRP_FLAG': {0: None, 1: None, 2: None, 3: None, 4: None},
            'PDRP_DATE': {0: None, 1: None, 2: None, 3: None, 4: None},
            'POLO_ADDR2': {0: None, 1: None, 2: None, 3: None, 4: None},
            'POLO_ADDR1': {0: None,
                           1: '20 YORK ST',
                           2: '3551 ROGER BROOKE DR',
                           3: None,
                           4: None},
            'POLO_CITY': {0: None, 1: 'NEW HAVEN', 2: 'JBSA FSH', 3: None, 4: None},
            'POLO_STATE': {0: None, 1: 'CT', 2: 'TX', 3: None, 4: None},
            'POLO_ZIP': {0: None, 1: '06510', 2: '78234', 3: None, 4: None},
            'POLO_PLUS4': {0: None, 1: '3220', 2: '4504', 3: None, 4: None},
            'POLOCARRIERROUTE': {0: None, 1: 'C098 ', 2: 'C054 ', 3: None, 4: None},
            'MOSTRECENTFORMERLASTNAME': {0: None, 1: None, 2: None, 3: None, 4: None},
            'MOSTRECENTFORMERMIDDLENAME': {0: None, 1: None, 2: None, 3: None, 4: None},
            'MOSTRECENTFORMERFIRSTNAME': {0: None, 1: None, 2: None, 3: None, 4: None},
            'NEXTMOSTRECENTFORMERLASTNAME': {0: None, 1: None, 2: None, 3: None, 4: None},
            'NEXTMOSTRECENTFORMERMIDDLENAME': {0: None,
                                               1: None,
                                               2: None,
                                               3: None,
                                               4: None},
            'NEXTMOSTRECENTFORMERFIRSTNAME': {0: None,
                                              1: None,
                                              2: None,
                                              3: None,
                                              4: None},
            'JOB_ID': {0: None, 1: None, 2: None, 3: None, 4: None},
            'CURRENT_BATCH_FLAG': {0: None, 1: None, 2: None, 3: None, 4: None},
            'BATCH_BUSINESS_DATE': {0: None, 1: None, 2: None, 3: None, 4: None}}

    return [pandas.DataFrame.from_dict(data)]


@pytest.fixture
def environment(extractor_file, loader_directory):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.jdbc.test_extract.Extractor'
    os.environ['EXTRACTOR_DATABASE_NAME'] = 'eprdods'
    # os.environ['EXTRACTOR_DATABASE_USERNAME'] = <set manually in environment>
    # os.environ['EXTRACTOR_DATABASE_PASSWORD'] = <set manually in environment>
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'rdbp1190'
    os.environ['EXTRACTOR_DATABASE_PORT'] = '54150'

    os.environ['EXTRACTOR_SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE LIMIT 20;'
    os.environ['EXTRACTOR_DRIVER'] = 'com.ibm.db2.jcc.DB2Driver'
    os.environ['EXTRACTOR_DRIVER_TYPE'] = 'db2'
    os.environ['EXTRACTOR_JAR_PATH'] = './db2jcc4.jar'

    os.environ['TRANSFORMER_CLASS'] = 'datalabs.etl.oneview.ppd.transform.PPDTransformer'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
