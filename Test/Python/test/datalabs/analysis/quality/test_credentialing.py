""" Unit test for datalabs.analysis.quality.credentialing"""
from io import BytesIO

import pandas
import pytest

from datalabs.analysis.quality.credentialing import (
    NpiRegistrationCompletenessTransformerTask,
    DeaRegistrationCompletenessTransformerTask,
    CertificatesCompletenessTransformerTask,
    LicenseCompletenessTransformerTask,
)


# pylint: disable=redefined-outer-name, protected-access
def test_npi_registration_completeness_transformer_task(parameters):
    task = NpiRegistrationCompletenessTransformerTask(parameters)

    result = task._parse_input(task._parameters["data"])

    npi_registration_completeness = task._create_npi_registration_completeness(result)

    assert len(result) == 2
    assert isinstance(result[0], pandas.DataFrame)
    assert isinstance(result[1], pandas.DataFrame)

    assert npi_registration_completeness[0].element.unique().tolist() == ["col1", "col2", "col3"]
    assert len(npi_registration_completeness[0]) == 9


def test_dea_registration_completeness_transformer_task(parameters):
    task = DeaRegistrationCompletenessTransformerTask(parameters)

    result = task._parse_input(task._parameters["data"])

    dea_registration_completeness = task._create_dea_registration_completeness(result)

    assert len(result) == 2
    assert isinstance(result[0], pandas.DataFrame)
    assert isinstance(result[1], pandas.DataFrame)

    assert dea_registration_completeness[0].element.unique().tolist() == ["col1", "col2", "col3"]
    assert len(dea_registration_completeness[0]) == 9


def test_certificates_completeness_transformer_task(parameters):
    task = CertificatesCompletenessTransformerTask(parameters)

    result = task._parse_input(task._parameters["data"])

    certificates_completeness = task._create_certificates_completeness(result)

    assert len(result) == 2
    assert isinstance(result[0], pandas.DataFrame)
    assert isinstance(result[1], pandas.DataFrame)

    assert certificates_completeness[0].element.unique().tolist() == ["col1", "col2", "col3"]
    assert len(certificates_completeness[0]) == 9


def test_license_completeness_transformer_task(parameters):
    task = LicenseCompletenessTransformerTask(parameters)

    result = task._parse_input(task._parameters["data"])

    license_completeness = task._create_license_completeness(result)

    assert len(result) == 2
    assert isinstance(result[0], pandas.DataFrame)
    assert isinstance(result[1], pandas.DataFrame)

    assert license_completeness[0].element.unique().tolist() == ["col1", "col2", "col3"]
    assert len(license_completeness[0]) == 9


@pytest.fixture
def parameters(data):
    return dict(data=data, EXECUTION_TIME="2023-11-08T21:30:00.000000")


@pytest.fixture
def data(credentialing_entity, measurement_method_configuration):
    data = [credentialing_entity, measurement_method_configuration]

    return data


@pytest.fixture
def credentialing_entity():
    data = b"""medical_education_number,col1,col2,col3\n
    100,Nan,2,4\n
    101,1,Nan,5\n
    102,Nan,3,6\n"""

    return data


@pytest.fixture
def measurement_method_configuration():
    data = {
        "condition_value": [False, False, False],
        "value": ["Nan", "", ""],
        "column_name": ["col1", "col2", "col3"],
        "measure": ["completeness", "completeness", "completeness"],
        "data_type": ["credentials", "credentials", "credentials"],
        "condition_indicator": [False, False, False],
    }
    measurement_method_configuration = pandas.DataFrame(data)
    excel_buffer = BytesIO()
    measurement_method_configuration.to_excel(excel_buffer, index=False)
    excel_data = excel_buffer.getvalue()

    return excel_data
