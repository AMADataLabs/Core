""" source: datalabs.etl.vericre.profile.transform """
from   io import StringIO
import pickle

import pandas
import pytest

from   datalabs.etl.vericre.profile import transform
from   datalabs.etl.vericre.profile import column


# pylint: disable=redefined-outer-name, protected-access
def test_demographics_data_populated(demographics_data):
    transformer = transform.AMAProfileTransformerTask(parameters={})

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
