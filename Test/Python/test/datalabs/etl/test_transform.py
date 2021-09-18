""" source: datalabs.etl.transform """
from   io import BytesIO
import os
import pathlib
import pytest
import tempfile

import dask.array
import pandas

from datalabs.etl.transform import TransformerTask, PassThroughTransformerTask, ScalableTransformerMixin


# pylint: disable=redefined-outer-name
def test_transformer_task(transformer):
    transformer.run()

    assert transformer.data == 'True'


def test_pass_through_transformer():
    transformer = PassThroughTransformerTask(dict(data='True'))

    transformer.run()


    assert transformer.data


# pylint: disable=protected-access
def test_scalable_dataframes_mixin_in_memory(csv_file):
    on_disk = False
    with open(csv_file, 'rb') as csv:
        input_data = ScalableTransformerMixin._csv_to_dataframe(csv.read(), on_disk)
    new_column = ['00', '11', '22', '33', '44', '55', '66', '77', '88', '99', 'R2']

    input_data.id = new_column

    output_data = pandas.read_csv(BytesIO(ScalableTransformerMixin._dataframe_to_csv(input_data, on_disk)))

    assert all(output_data.id == new_column)


# pylint: disable=protected-access
def test_scalable_dataframes_mixin_on_disk(csv_file):
    on_disk = True
    input_data = ScalableTransformerMixin._csv_to_dataframe(csv_file, on_disk)
    new_column = ['00', '11', '22', '33', '44', '55', '66', '77', '88', '99', 'R2']

    input_data.id = dask.array.from_array(new_column)

    path = ScalableTransformerMixin._dataframe_to_csv(input_data, on_disk).decode()

    output_data = pandas.read_csv(path)

    assert all(output_data.id == new_column)

    os.remove(path)


@pytest.fixture
def transformer():
    return Transformer(dict(data='True'))


@pytest.fixture
def cache_directory():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


@pytest.fixture
def csv_file(cache_directory):
    path = pathlib.Path(cache_directory, "sample_data.csv")

    with open(path, 'wb') as file:
        file.write(b'''name,id
foo,12345
bar,54321
ping,12345
pong,54321
biff,12345
baff,54321
ding,12345
dong,54321
pitter,12345
patter,54321
boing,Q101
'''
        )

    return bytes(path)


class Transformer(TransformerTask):
    def _transform(self):
        return str(self._parameters['data'])
