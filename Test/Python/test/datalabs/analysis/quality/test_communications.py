""" Unit test for datalabs.analysis.quality.communications"""
from io import BytesIO

import pandas
import pytest

from datalabs.analysis.quality.communications import PartyLevelCompleteness


# pylint: disable=redefined-outer-name, protected-access
def test_party_level_completeness_transformer_task(parameters):
    task = PartyLevelCompleteness(parameters)

    result = task._parse_input(task._parameters["data"])

    party_level_completeness = task._create_party_level_completeness(result)

    assert len(result) == 2
    assert isinstance(result[0], pandas.DataFrame)
    assert isinstance(result[1], pandas.DataFrame)

    assert party_level_completeness[0].element.unique().tolist() == ["col1", "col2", "col3", "medical_education_number"]
    assert len(party_level_completeness[0]) == 12


@pytest.fixture
def parameters(data):
    return dict(data=data, EXECUTION_TIME="2023-11-08T21:30:00.000000")


@pytest.fixture
def data(communications_entity, measurement_method_configuration):
    data = [communications_entity, measurement_method_configuration]

    return data


@pytest.fixture
def communications_entity():
    data = b"""medical_education_number,col1,col2,col3\n
    100,Nan,2,4\n
    101,1,Nan,5\n
    102,Nan,3,6\n"""

    return data


@pytest.fixture
def measurement_method_configuration():
    data = {
        "condition_value": [False, False, False, False],
        "value": ["Nan", "", "", ""],
        "column_name": ["col1", "col2", "col3", "medical_education_number"],
        "measure": ["completeness", "completeness", "completeness", "completeness"],
        "data_type": ["contact", "contact", "contact", "contact"],
        "condition_indicator": [False, False, False, False],
    }
    measurement_method_configuration = pandas.DataFrame(data)
    excel_buffer = BytesIO()
    measurement_method_configuration.to_excel(excel_buffer, index=False)
    excel_data = excel_buffer.getvalue()

    return excel_data
