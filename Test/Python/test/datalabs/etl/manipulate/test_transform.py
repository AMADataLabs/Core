""" source: datalabs.etl.manipulate.transform """
from   io import BytesIO

import pandas
import pytest

from datalabs.etl.manipulate.transform import ConcatenateTransformerTask, DateFormatTransformerTask


# pylint: disable=redefined-outer-name
def test_concatenation_works_on_indexed_csv(split_indexed_data):
    task = ConcatenateTransformerTask(dict(execution_time='2021-01-01 00:00:00'), split_indexed_data)
    data = task.run()

    assert len(data) == 1

    concatenated_data = pandas.read_csv(BytesIO(data[0]), dtype=object)  # pylint: disable=unsubscriptable-object

    assert len(concatenated_data) == 4


# pylint: disable=redefined-outer-name
def test_concatenation_works_on_unindexed_csv(split_unindexed_data):
    task = ConcatenateTransformerTask(dict(execution_time='2021-01-01 00:00:00'), split_unindexed_data)

    data = task.run()

    assert len(data) == 1

    concatenated_data = pandas.read_csv(BytesIO(data[0]), dtype=object)  # pylint: disable=unsubscriptable-object

    assert len(concatenated_data) == 4


# pylint: disable=redefined-outer-name
def test_date_reformatting_works(nonstandard_date_data, standard_date_data):
    task = DateFormatTransformerTask(dict(columns="COLUMN1, COLUMN3 ", input_format="%M/%d/%Y"), nonstandard_date_data)

    data = task.run()

    assert data == standard_date_data


@pytest.fixture
def split_indexed_data():
    return [
        b',COLUMN1,COLUMN2,COLUMN3\n0,INS00000004,INTALERE,\n1,INS00000008,CHILDRENS HOSPITAL ASSOCIATION,\n',
        b',COLUMN1,COLUMN2,COLUMN3\n0,INS00000010,FUNKY TOWN,\n1,INS00000011,FOREVERMORE DANCE,\n'
    ]


@pytest.fixture
def split_unindexed_data():
    return [
        b'COLUMN1,COLUMN2,COLUMN3\nINS00000004,INTALERE,\nINS00000008,CHILDRENS HOSPITAL ASSOCIATION,\n',
        b'COLUMN1,COLUMN2,COLUMN3\nINS00000010,FUNKY TOWN,\nINS00000011,FOREVERMORE DANCE,\n'
    ]


@pytest.fixture
def nonstandard_date_data():
    return [
        b'COLUMN1,COLUMN2,COLUMN3\n12/29/1977,foo,01/22/2002\n06/11/2254,bar,11/09/1999\n',
        b'COLUMN1,COLUMN2,COLUMN3\n,foo,11/20/2000\n04/09/2252,bar,09/07/1997\n',
    ]


@pytest.fixture
def standard_date_data():
    return [
        b'COLUMN1,COLUMN2,COLUMN3\n1977-12-29,foo,2002-01-22\n2254-06-11,bar,1999-11-09\n',
        b'COLUMN1,COLUMN2,COLUMN3\n,foo,2000-11-20\n2252-04-09,bar,1997-09-07\n',
    ]
