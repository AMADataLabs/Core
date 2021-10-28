""" source: datalabs.etl.manipulate.transform """
from   io import BytesIO

import pandas
import pytest

from datalabs.etl.manipulate.transform import ConcatenateTransformerTask


# pylint: disable=redefined-outer-name
def test_concatenation_works_on_indexed_csv(split_indexed_data):
    task = ConcatenateTransformerTask(dict(execution_time='2021-01-01 00:00:00', data=split_indexed_data))
    task.run()

    assert len(task.data) == 1

    concatenated_data = pandas.read_csv(BytesIO(task.data[0]), dtype=object)  # pylint: disable=unsubscriptable-object

    assert len(concatenated_data) == 4


# pylint: disable=redefined-outer-name
def test_concatenation_works_on_unindexed_csv(split_unindexed_data):
    task = ConcatenateTransformerTask(dict(execution_time='2021-01-01 00:00:00', data=split_unindexed_data))
    task.run()

    assert len(task.data) == 1

    concatenated_data = pandas.read_csv(BytesIO(task.data[0]), dtype=object)  # pylint: disable=unsubscriptable-object

    assert len(concatenated_data) == 4


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
