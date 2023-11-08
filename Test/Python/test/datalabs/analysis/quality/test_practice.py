""" source: datalabs.analysis.quality.person """
from io import BytesIO

import pandas
import pytest

from datalabs.analysis.quality.practice import CompletenessTransformerTask


# pylint: disable=redefined-outer-name, protected-access
@pytest.fixture
def parameters(data):
    return dict(data=data, EXECUTION_TIME="2023-11-08T21:30:00.000000")


@pytest.fixture
def data(practice_entity, measurement_method_configuration):
    data = [practice_entity, measurement_method_configuration]

    return data


@pytest.fixture
def practice_entity():
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
        "data_type": ["practice", "practice", "practice"],
        "condition_indicator": [False, False, False],
    }
    measurement_method_configuration = pandas.DataFrame(data)

    excel_buffer = BytesIO()

    measurement_method_configuration.to_excel(excel_buffer, index=False)

    excel_data = excel_buffer.getvalue()

    return excel_data


@pytest.fixture
def transformer(parameters):
    return CompletenessTransformerTask(parameters)


def test_parse_input(transformer, data):
    input_data = transformer._parse_input(data)

    assert len(input_data) == 2
    assert isinstance(input_data[0], pandas.DataFrame)
    assert isinstance(input_data[1], pandas.DataFrame)


def test_create_practice_completeness(transformer, data):
    input_data = transformer._parse_input(data)
    practice_completeness = transformer._create_practice_completeness(input_data)
    practice_completeness = practice_completeness[0]

    assert practice_completeness.element.unique().tolist() == ["col1", "col2", "col3"]
    assert len(practice_completeness) == 9
