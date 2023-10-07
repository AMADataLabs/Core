""" source: datalabs.etl.vericre.profile.transform """
from   io import StringIO
import pickle

import pandas
import pytest

from   datalabs.etl.vericre.profile import transform
from   datalabs.etl.vericre.profile import column


# pylint: disable=redefined-outer-name, protected-access
def test_sanctions_data_populated(sanctions_data):
    transformer = transform.SanctionsTransformerTask(parameters={})

    vericre_profiles = transformer._create_sanctions(sanctions_data)

    _assert_correct_sanctions_count(vericre_profiles)

    _assert_sanctions_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_licenses_data_populated(licenses_data):
    transformer = transform.LicensesTransformerTask(parameters={})

    vericre_profiles = transformer._create_licenses(licenses_data)

    _assert_correct_licenses_count(vericre_profiles)

    _assert_licenses_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_medical_training_data_populated(medical_training_data):
    transformer = transform.MedicalTrainingTransformerTask(parameters={})

    vericre_profiles = transformer._create_medical_training(medical_training_data)

    _assert_correct_medical_training_count(vericre_profiles)

    _assert_medical_training_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_abms_data_populated(abms_data):
    transformer = transform.ABMSTransformerTask(parameters={})

    vericre_profiles = transformer._create_abms(abms_data)

    _assert_correct_abms_count(vericre_profiles)

    _assert_abms_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_medical_schools_data_populated(medical_schools_data):
    transformer = transform.MedicalSchoolsTransformerTask(parameters={})

    vericre_profiles = transformer._create_medical_schools(medical_schools_data)

    _assert_correct_medical_schools_count(vericre_profiles)

    _assert_medical_schools_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_npi_data_populated(npi_data):
    transformer = transform.NPITransformerTask(parameters={})

    vericre_profiles = transformer._create_npi(npi_data)

    _assert_correct_npi_count(vericre_profiles)

    _assert_npi_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_dea_data_populated(dea_data):
    transformer = transform.DeaTransformerTask(parameters={})

    vericre_profiles = transformer._create_dea(dea_data)

    _assert_correct_dea_count(vericre_profiles)

    _assert_dea_fields_populated(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_demographics_data_populated(demographics_data):
    transformer = transform.DemographicsTransformerTask(parameters={})

    vericre_profiles = transformer._create_demographics(demographics_data)

    _assert_correct_demographics_count(vericre_profiles)

    _assert_demographics_fields_populated(vericre_profiles)

    _assert_demographics_print_name_comprises_first_and_last_name(vericre_profiles)

    _assert_demographics_phone_comprises_aread_code_exchange_and_number(vericre_profiles)

    _assert_demographics_phone_is_null_if_any_components_are_null(vericre_profiles)


# pylint: disable=redefined-outer-name, protected-access
def test_caqh_status_url_list_transformer_task(ama_masterfile_data):
    host = 'example.org'
    organization_id = '123'
    base_url = f'https://{host}/RosterAPI/api/providerstatusbynpi'
    common_params = f'Product=PV&Organization_Id={organization_id}'
    npi_code_1 = '123456009'
    npi_code_2 = '123456008'
    npi_code_3 = '123456007'

    url_1 = f'{base_url}?{common_params}&NPI_Provider_Id={npi_code_1}\n'
    url_2 = f'{base_url}?{common_params}&NPI_Provider_Id={npi_code_2}\n'
    url_3 = f'{base_url}?{common_params}&NPI_Provider_Id={npi_code_3}'

    expected_urls = [url_1.encode() + url_2.encode() + url_3.encode()]

    task = transform.CAQHStatusURLListTransformerTask(
        parameters=dict(host=host, organization=organization_id),
        data=ama_masterfile_data
    )

    result = task.run()

    assert result == expected_urls


# pylint: disable=redefined-outer-name
def test_caqh_url_list_transformer_task(caqh_profile_statuses):
    host = 'example.org'

    organization_id = '6167'
    url_1 = (
        "https://example.org/credentialingapi/api/v8/entities?"
        "organizationId=6167&caqhProviderId=16038676&attestationDate=08/14/2022"
    )

    expected_urls = [url_1.encode()]

    task = transform.CAQHProfileURLListTranformerTask(
        parameters=dict(host=host, organization=organization_id),
        data=caqh_profile_statuses
    )

    result = task.run()

    assert result == expected_urls


def _assert_correct_sanctions_count(vericre_profiles):
    assert len(vericre_profiles) == 4

    assert len(vericre_profiles.iloc[1]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "sanctions" in vericre_profiles.iloc[0]


def _assert_sanctions_fields_populated(vericre_profiles):
    expected_fields = column.SANCTIONS_COLUMNS
    sanctions = vericre_profiles.iloc[0].sanctions

    assert len(sanctions) == len(expected_fields) * 2 - 1

    for sanction_column in expected_fields:
        assert sanction_column in sanctions

        if sanction_column != "federalSanctions":
            assert f'{sanction_column}Value' in sanctions


def _assert_correct_licenses_count(vericre_profiles):
    assert len(vericre_profiles) == 2

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "licenses" in vericre_profiles.iloc[0]


def _assert_licenses_fields_populated(vericre_profiles):
    expected_fields = column.LICENSES_COLUMNS.values()
    licenses = vericre_profiles.iloc[0].licenses

    assert len(licenses[0]) == len(expected_fields) + 1

    for licenses_column in expected_fields:
        assert licenses_column in licenses[0]

    assert 'licenseName' in licenses[0]


def _assert_correct_medical_training_count(vericre_profiles):
    assert len(vericre_profiles) == 1

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "medicalTraining" in vericre_profiles.iloc[0]


def _assert_medical_training_fields_populated(vericre_profiles):
    expected_fields = column.MEDICAL_TRAINING_COLUMNS.values()
    medical_training = vericre_profiles.iloc[0].medicalTraining[0]

    assert len(medical_training) == len(expected_fields)

    for medical_column in expected_fields:
        assert medical_column in medical_training


def _assert_correct_abms_count(vericre_profiles):
    assert len(vericre_profiles) == 1

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "abms" in vericre_profiles.iloc[0]


def _assert_abms_fields_populated(vericre_profiles):
    expected_fields = column.ABMS_COLUMNS.values()
    abms = vericre_profiles.iloc[0].abms[0]

    assert len(abms) == len(expected_fields) + 1

    for abms_column in expected_fields:
        assert abms_column in abms

    assert 'disclaimer' in abms


def _assert_correct_medical_schools_count(vericre_profiles):
    assert len(vericre_profiles) == 2

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "medicalSchools" in vericre_profiles.iloc[0]


def _assert_medical_schools_fields_populated(vericre_profiles):
    expected_fields = column.MEDICAL_SCHOOL_COLUMNS.values()
    medical_schools = vericre_profiles.iloc[0].medicalSchools

    assert len(medical_schools[0]) == len(expected_fields) + 1

    for medical_schools_column in expected_fields:
        assert medical_schools_column in medical_schools[0]

    assert 'medicalEducationType' in  medical_schools[0]


def _assert_correct_npi_count(vericre_profiles):
    assert len(vericre_profiles) == 7

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "npi" in vericre_profiles.iloc[0]


def _assert_npi_fields_populated(vericre_profiles):
    expected_fields = column.NPI_COLUMNS.values()
    npi = vericre_profiles.iloc[0].npi

    assert len(npi) == len(expected_fields)

    for npi_column in expected_fields:
        assert npi_column in npi


def _assert_correct_dea_count(vericre_profiles):
    assert len(vericre_profiles) == 2

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "dea" in vericre_profiles.iloc[0]


def _assert_dea_fields_populated(vericre_profiles):
    expected_fields = column.DEA_COLUMNS.values()
    dea = vericre_profiles.iloc[0].dea

    assert len(dea[0]) == len(expected_fields) + 1

    for dea_column in expected_fields:
        assert dea_column in dea[0]

    assert 'address' in dea[0]


def _assert_correct_demographics_count(vericre_profiles):
    assert len(vericre_profiles) == 2

    assert len(vericre_profiles.iloc[0]) == 2
    assert "entityId" in vericre_profiles.iloc[0]
    assert "demographics" in vericre_profiles.iloc[0]


def _assert_demographics_fields_populated(vericre_profiles):
    expected_fields = column.DEMOGRAPHICS_COLUMNS.values()
    demographics = vericre_profiles.iloc[0].demographics

    assert vericre_profiles.iloc[0].entityId == "1234567"

    assert len(demographics) == len(expected_fields)

    for demographic_column in expected_fields:
        assert demographic_column in demographics


def _assert_demographics_print_name_comprises_first_and_last_name(vericre_profiles):
    demographics = vericre_profiles.iloc[0].demographics
    first_name = demographics["firstName"]
    last_name = demographics["lastName"]
    print_name = demographics["printName"]

    assert print_name == f"{first_name} {last_name}"


def _assert_demographics_phone_comprises_aread_code_exchange_and_number(vericre_profiles):
    demographics = vericre_profiles.iloc[0].demographics
    print_number = demographics["phone"]["phoneNumber"]
    area_code = demographics["phone"]["areaCode"]
    exchange = demographics["phone"]["exchange"]
    number = demographics["phone"]["number"]

    assert print_number == f"{area_code}{exchange}{number}"


# pylint: disable=comparison-with-itself
def _assert_demographics_phone_is_null_if_any_components_are_null(vericre_profiles):
    ''' Check that area code is NaN and that a null phone number results. '''
    demographics = vericre_profiles.iloc[1].demographics
    print_number = demographics["phone"]["phoneNumber"]
    area_code = demographics["phone"]["areaCode"]
    exchange = demographics["phone"]["exchange"]
    number = demographics["phone"]["number"]

    assert area_code != area_code
    assert exchange
    assert number
    assert print_number is None


@pytest.fixture
def sanctions_data():
    raw_data = """
ENTITY_ID|BOARD_CD|BOARD_DESC
1|ZF|US Air Force
1|ZF|US Air Force
3|ZF|US Air Force
4|ZF|US Air Force
5|ZF|US Air Force
5|ZF|US Air Force
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def licenses_data():
    raw_data = """
ENTITY_ID|LIC_NBR|LIC_ISSUE_DT|LIC_EXP_DT|LIC_RNW_DT|LIC_AS_OF_DT|LIC_TYPE_DESC|LIC_STATE_DESC|DEGREE_CD|STATE_SANCTIONS|LIC_STATUS_DESC|FIRST_NAME|MIDDLE_NAME|LAST_NAME|STATE_CD|RPTD_LICENSE_NBR|RPTD_SFX_NM|RPTD_FULL_NM
1|12345600|1999-07-01|2014-05-31|2014-01-02|2013-04-21|Unlimited|Missouri|MD|N|Active|Brian|E|Meyer|MO|12345600X||Brian E Meyer MD
1|12346600|2004-07-01|2014-12-31|2014-01-02|2013-06-30|Unlimited|California|MD|N|Active|Brian|E|Meyer|CA|12346600X||Brian E Meyer MD
2|12345601|1999-07-01|2014-05-31|2014-01-02|2013-04-21|Unlimited|California|MD|N|Inactive|Jeffrey|R|Conaway|CA|12345601X||Jeffrey R Conaway MD
2|12346601|2004-07-01|2014-12-31|2014-01-02|2013-06-30|Unlimited|Washington|MD|N|Active|Jeffrey|R|Conaway|WA|12346601X||Jeffrey R Conaway MD
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def medical_training_data():
    raw_data = """
ENTITY_ID|PRIMARY_SPECIALITY|SECONDARY_SPECIALTY|INST_NAME|INST_STATE|BEGIN_DT|END_DT|BEGIN_DT_DESC|END_DT_DESC|NBR_MONTHS|CONFIRM_STATUS|INC_MSG|INC_FLAG|PROGRAM_NM|HOSPITAL_ID|AMA_INST_CODE|PROGRAM_CODE|INCOMPLETE_FLAG|TRAINING_TYPE
1|CARDIOVASCULAR DISEASE|UNDEFINED|LA STATE UNIV HP-SHREVEPORT-1|LOUISIANA|2001-07-01|2004-06-01|Begin-1|End-1|23|VERIFICATION OF COMPLETION IN PROGRESS|Inc Msg|Y|LA SHREVEPORT PROGRAM|||1104112043|Y|
1|INTERNAL MEDICINE|UNDEFINED|LA STATE UNIV HP-SHREVEPORT-1|LOUISIANA|1999-07-01|2001-06-01|Begin-1|End-1|23|VERIFICATION OF COMPLETION IN PROGRESS|Inc Msg|Y|LA SHREVEPORT PROGRAM|||1104112043|Y|
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def abms_data():
    raw_data = """
ENTITY_ID|CERT_BOARD|CERTIFICATE|CERTIFICATE_TYPE|EFFECTIVE_DT|EXPIRATION_DT|LAST_REPORTED_DT|CERT_STAT_DESC|DURATION_TYPE_DESC|MOC_MET_RQT|REACTIVATION_DT|CERTIFICATION_ID|ABMS_BIO_ID|MOC_PATHWAY_BRD_MSG|MOC_PATHWAY_ID|ABMS_RECORD_TYPE
1|AMERICAN BOARD OF FAMILY PRACTICE-1|FAMILY PRACTICE-1|General|2001-01-01|2012-12-31|2013-10-10|Initial Certification|Lifetime|Y|2013-10-10|123456000||||Expired
1|AMERICAN BOARD OF FAMILY PRACTICE-1|FAMILY PRACTICE-1|General|1994-01-01|2002-12-31|2013-10-10|Initial Certification|Lifetime|Y|2013-10-10|123457000||||Expired
1|AMERICAN BOARD OF FAMILY PRACTICE-1|FAMILY PRACTICE-1|General|1987-01-01|2002-12-31|2013-10-10|Initial Certification|Lifetime|Y|2013-10-10|123458000||||Expired
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def medical_schools_data():
    raw_data = """
ENTITY_ID|LABEL_FLAG|GRAD_STATUS|SCHOOL_NAME|GRAD_DT|SCHOOL_CD|CITY|STATE_CD|ZIP|AMA_SCHOOL_CD|SEGMENT_ONLY_IND|COUNTRY_NAME|MATRICULATION_DT|DEGREE_CD|NSC_IND
1|Y|YES|LAKE ERIE COLL OF OSTEO MED|1998-05-10|04178|Erie|PA|16509|14797870||United States of America|1995-05-10|MD|N
1|Y|YES|LAKE ERIE COLL OF OSTEO MED|1996-05-10|04178|Erie|PA|16509|14797870||United States of America|1993-05-10|MD|N
2|Y|Yes|TOURO UNIV COLL OF OSTEO MED, VALLEJO CA 94592|1998-05-10|00577|Vallejo|CA|94592|14795049||United States of America|1995-05-10|MD|N
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def npi_data():
    raw_data = """
ENTITY_ID|NPI_CD|ENUMERATION_DT|DEACTIVATION_DT|REACTIVATION_DT|REP_NPI_CD|RPTD_DT|FIRST_NAME|MIDDLE_NAME|LAST_NAME
1|123456000|2001-06-30|2014-01-01|2012-01-01|1234507891|2013-05-30|Brian|E|Meyer
2|123456001|2001-06-30|2014-01-01|2012-01-01|1234507892|2013-05-30|Jeffrey|R|Conaway
3|123456002|2001-06-30|2014-01-01|2012-01-01|1234507893|2013-05-30|Tamara|C|Suslov
4|123456003|2001-06-30|2014-01-01|2012-01-01|1234507894|2013-05-30|Raymond|E|Bellamy
5|123456004|2001-06-30|2014-01-01|2012-01-01|1234507895|2013-05-30|Stuart||Davidson
6|123456005|2001-06-30|2014-01-01|2012-01-01|1234507896|2013-05-30|R|Barry|Engrahm
7|123456006|2001-06-30|2014-01-01|2012-01-01|1234507897|2013-05-30|Horace|B|Gardner
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def dea_data():
    raw_data = """
ENTITY_ID|DEA_NBR|DEA_SCHEDULE|DEA_AS_OF_DT|DEA_EXPR_DT|DEA_STATUS|DEA_STATUS_DESC|COMM_ID|ADDRESS_LINE_1|ADDRESS_LINE_2|ADDRESS_LINE_3|CITY_NM|STATE_ID|ZIP|COUNTRY_NM|RENEWEL_DT|FIRST_NAME|MIDDLE_NAME|LAST_NAME|BUSINESS_ACTIVITY_SUBCODE|BUSINESS_ACTIVITY_CODE|PAYMENT_IND
1|AB3456000|22N 33N 4 5|2013-04-30|2014-11-01|A|Active|1234|123 Main Street|test_addr_line2|test_addr_line3|Anycity|IL|12345-9876|USA||Brian|E|Meyer|2|C|EXEMPT
1|AB3457000|2N 33N 4 5|2013-04-30|2014-11-01|A|Active|1234|123 Main Street|test_addr_line2|test_addr_line3|Anycity|IL|12345-9876|USA||Brian|E|Meyer|2|C|EXEMPT
2|AB3456001|22N 33N 4 5|2013-04-30|2014-11-01|A|Active|1234|123 Main Street|test_addr_line2|test_addr_line3|Anycity|IL|12345-9876|USA||Jeffrey|R|Conaway|3|C|
2|AB3457001|2N 33N 4 5|2013-04-30|2014-11-01|A|Active|1234|123 Main Street|test_addr_line2|test_addr_line3|Anycity|IL|12345-9876|USA||Jeffrey|R|Conaway|3|C|
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def demographics_data():
    raw_data = """
DEMOG_DATA_ID|ENTITY_ID|MAILING_COMM_ID|MAILING_ADDRESS_LINE_1|MAILING_ADDRESS_LINE_2|MAILING_ADDRESS_LINE_3|MAILING_CITY_NM|MAILING_STATE_ID|MAILING_ZIP|MAILING_COUNTRY_NM|POLO_COMM_ID|POLO_ADDRESS_LINE_1|POLO_ADDRESS_LINE_2|POLO_ADDRESS_LINE_3|POLO_CITY_NM|POLO_STATE_ID|POLO_ZIP|POLO_COUNTRY_NM|COMM_ID|PHONE_PREFIX|PHONE_AREA_CD|PHONE_EXCHANGE|PHONE_NUMBER|PHONE_EXTENSION|LABEL_NAME|BIRTH_DT|BIRTH_PLACE|ME_NBR|FAX_COMM_ID|FAX_PREFIX|FAX_AREA_CD|FAX_EXCHANGE|FAX_NUMBER|FAX_EXTENSION|EMAIL_NAME|EMAIL_DOMAIN|MORTALITY_STATUS|DEATH_DT|STUDENT_IND|ADDR_UNDELIVERABLE_IND|ME_RPT_IND|COMM_DISP_IND|NO_RELEASE_IND|ADDTL_INFO_IND|CUT_IND|MPA_DESC|STATUS_DESC|ECFMG_NBR|PRA_EXPR_DT|DEGREE_CD|NAT_BRD_YEAR|LAS_BOARD_CD|LS_LICENSE_SANC|LS_LICENSE_SANC_STATE|ADDTL_FLAG|FED_SANCTIONS_IND|FOOTER_LABEL_NAME|PRIMARY_SPECIALTY|SECONDARY_SPECIALTY|NAME_PREFIX|FIRST_NAME|MIDDLE_NAME|LAST_NAME|NAME_SUFFIX|NAT_BOARD_DESC|NO_CONT_PHONE_IND|NO_CONT_FAX_IND|NO_CONT_MAILING_IND|MAILING_TYPE|GENDER|TYPE_OF_PRACTICE|PRESENT_EMP|BIRTH_COUNTRY|PDRP_FLAG|PRIMARY_SPEC_CODE|SECONDARY_SPEC_CODE|PERSON_TYPE|NO_CONTACT_IND
12345678|1234567|12345678|221B Backer St|Marylebone||London|England|NW1 6XE|United Kingdom|12345678|221B Backer St|Marylebone||London|England|NW1 6XE|United Kingdom|12345678|44|207|946|0346||William Sherlock Scott Holmes MD|1854-01-06|London,England United Kingdom|12345678901|12345678|44|207|946|0346||masterdetective|doyle.com|||N|N|||N||N|Hospital Based Full-Time Physician Staff|Member|||MD|0||||||William Scott Sherlock Holmes|INTERNAL MEDICINE|UNSPECIFIED||Sherlock|S|Holmes|||N|N|N|HM|M|Direct Patient Care|Government Hospital|United Kingdom|N|IM|US|P|N
12345679|1234568|12345679|221B Backer St|Marylebone||London|England|NW1 6XE|United Kingdom|12345678|221B Backer St|Marylebone||London|England|NW1 6XE|United Kingdom|12345678|1||555|5432||Bob Villa MD|1854-01-06|London,England United Kingdom|12345678901|12345678|1|123|555|4321||masterbuilder|pbs.org|||N|N|||N||N|Hospital Based Full-Time Physician Staff|Member|||MD|0||||||Bob Villa|INTERNAL MEDICINE|UNSPECIFIED||Bob|S|Villa|||N|N|N|HM|M|Direct Patient Care|Government Hospital|United Kingdom|N|IM|US|P|N
    """
    return pandas.read_csv(StringIO(raw_data), sep="|", dtype=object)


@pytest.fixture
def ama_masterfile_data():
    return [
        """
            [
                {
                    "npi": {
                        "npiCode": "123456009"
                    }
                },
                {
                    "npi": {
                        "npiCode": "123456008"
                    }
                },
                {
                    "npi": {
                        "npiCode": "123456007"
                    }
                }
            ]
        """.encode()
    ]


# pylint: disable=line-too-long
@pytest.fixture
def caqh_profile_statuses():
    return [
        pickle.dumps(
            [
                (
                    'https://proview-demo.nonprod.caqh.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=6166&NPI_Provider_Id=1669768537',
                    b'{"organization_id": "6166", "caqh_provider_id": "16113253", "roster_status": "NOT ON ROSTER", "provider_status": "Expired Attestation", "provider_status_date": "20220814", "provider_practice_state": "IL", "provider_found_flag": "Y"}'
                ),
                (
                    'https://proview-demo.nonprod.caqh.org/RosterAPI/api/providerstatusbynpi?Product=PV&Organization_Id=6166&NPI_Provider_Id=1669768538',
                    b'{"organization_id": "6167", "caqh_provider_id": "16038676", "roster_status": "ACTIVE", "provider_status": "Expired Attestation", "provider_status_date": "20220814", "provider_practice_state": "IL", "provider_found_flag": "Y"}'
                )
            ]
        )
    ]
