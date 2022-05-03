""" source: datalabs.etl.archive.transform """
from   io import BytesIO
import mock
import pickle
import pytest
# import tempfile
from   zipfile import ZipFile

import datalabs.etl.archive.transform as archive


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.order(0)
def test_zip_transformer_zips_tuple_data(zip_data):
    assert len(zip_data) == 1

    zip_file = ZipFile(BytesIO(zip_data[0]))
    filenames = zip_file.namelist()

    assert all([filename in filenames for filename in ['bogus.txt', 'bogus.bin']])


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.order(1)
def test_zip_transformer_zips_pickled_data(pickled_data):
    transformer = archive.ZipTransformerTask({"data": [pickled_data, pickled_data]})
    zip_datasets = transformer._transform()

    assert len(zip_datasets) == 2

    for zip_data in zip_datasets:
        zip_file = ZipFile(BytesIO(zip_data[0]))
        filenames = zip_file.namelist()

        assert all([filename in filenames for filename in ['bogus.txt', 'bogus.bin']])


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.order(1)
def test_unzip_transformer_extracts_all_files(zip_data, more_zip_data, file_data):
    transformer = archive.UnzipTransformerTask({"data": zip_data + more_zip_data})
    files = transformer._extract()

    assert len(files) == 4
    assert files[0] == file_data[0][1]
    assert files[1] == file_data[1][1]
    assert files[2] == file_data[0][1]
    assert files[3] == file_data[1][1]

@pytest.fixture
def file_data():
    return [
        ('bogus.txt', b'This is the way the world ends. Not with a bang but a whimper.'),
        ('bogus.bin', b'PK\x03\x04\n\x00\x00\x08\x08\x00')
    ]


@pytest.fixture
def pickled_data(file_data):
    return pickle.dumps(file_data)


@pytest.fixture
def zip_data(file_data):
    transformer = archive.ZipTransformerTask({"data": []})

    return transformer._zip_files(file_data)


@pytest.fixture
def more_zip_data():
    file_data = [
        ('bunk.txt', b'This is the way the world ends. Not with a bang but a whimper.'),
        ('bunk.bin', b'PK\x03\x04\n\x00\x00\x08\x08\x00')
    ]

    transformer = archive.ZipTransformerTask({"data": []})

    return transformer._zip_files(file_data)
