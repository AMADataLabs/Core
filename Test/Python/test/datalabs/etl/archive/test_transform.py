""" source: datalabs.etl.archive.transform """
from   io import BytesIO
import pickle
from   zipfile import ZipFile

import pytest

import datalabs.etl.archive.transform as archive


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.order(0)
def test_zip_transformer_zips_tuple_data(zip_data):
    assert len(zip_data) > 1

    with ZipFile(BytesIO(zip_data)) as zip_file:
        filenames = zip_file.namelist()

    assert all(filename in filenames for filename in ['bogus.txt', 'bogus.bin'])


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.order(1)
def test_zip_transformer_zips_pickled_data(pickled_data):
    transformer = archive.ZipTransformerTask({"data": [pickled_data, pickled_data]})
    zip_datasets = transformer.run(()

    assert len(zip_datasets) == 2

    for zip_data in zip_datasets:
        with ZipFile(BytesIO(zip_data)) as zip_file:
            filenames = zip_file.namelist()

        assert all(filename in filenames for filename in ['bogus.txt', 'bogus.bin'])


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.order(1)
def test_unzip_transformer_extracts_all_files(zip_data, more_zip_data, file_data, more_file_data):
    transformer = archive.UnzipTransformerTask({"data": [zip_data, more_zip_data]})
    files = transformer.run( )

    assert len(files) == 1

    named_files = pickle.loads(files[0])

    assert len(named_files) == 4
    assert named_files[0] == file_data[0]
    assert named_files[1] == file_data[1]
    assert named_files[2] == more_file_data[0]
    assert named_files[3] == more_file_data[1]

@pytest.fixture
def file_data():
    return [
        ('bogus.txt', b'This is the way the world ends. Not with a bang but a whimper.'),
        ('bogus.bin', b'PK\x03\x04\n\x00\x00\x08\x08\x00')
    ]

@pytest.fixture
def more_file_data():
    return [
        ('bunk.txt', b'This is the way the world ends. Not with a bang but a whimper.'),
        ('bunk.bin', b'PK\x03\x04\n\x00\x00\x08\x08\x00')
    ]


@pytest.fixture
def pickled_data(file_data):
    return pickle.dumps(file_data)


@pytest.fixture
def zip_data(file_data):
    transformer = archive.ZipTransformerTask({"data": []})

    return transformer._zip_files(file_data)


@pytest.fixture
def more_zip_data(more_file_data):
    transformer = archive.ZipTransformerTask({"data": []})

    return transformer._zip_files(more_file_data)
