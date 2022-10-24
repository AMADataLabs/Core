""" source: datalabs.etl.load """
import pytest

from datalabs.etl.load import FileLoaderTask


# pylint: disable=redefined-outer-name, protected-access
def test_files_data_length_mismatch_raises_error(file_loader):
    with pytest.raises(IndexError):
        file_loader._load_files([1, 2, 3], [1, 2])

    with pytest.raises(IndexError):
        file_loader._load_files([1, 2], [1, 2, 3])


@pytest.fixture
def file_loader():
    return FileLoader({}, [b'True'])


class FileLoader(FileLoaderTask):
    def _get_client(self):
        return None

    def _get_files(self):
        return None

    def _load_file(self, data, file):
        pass
