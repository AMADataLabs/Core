""" source: datalabs.etl.extract """
import pytest

from   dateutil.parser import isoparse

from datalabs.etl.extract import FileExtractorTask


def test_default_get_target_datetime(file_extractor, parameters):
    date = file_extractor._get_target_datetime()

    assert date == isoparse(parameters['EXECUTION_TIME'])


def test_resolve_timestamps(file_extractor, parameters):
    file_names = ["testfile1 - %Y-%m-%d.xlsx", "testfile2 - %Y-%m-%d.xlsx", "testfile3 - %Y-%m-%d.xlsx"]

    file_extractor._target_datetime = isoparse(parameters['EXECUTION_TIME'])
    files = file_extractor._resolve_timestamps(file_names)

    assert files == ["testfile1 - 1900-01-01.xlsx", "testfile2 - 1900-01-01.xlsx", "testfile3 - 1900-01-01.xlsx"]


@pytest.fixture
def file_extractor(parameters):
    return FileExtractor(parameters, [b'True'])


class FileExtractor(FileExtractorTask):
    def _get_client(self):
        return None

    def _get_files(self):
        return None

    def _extract_file(self, file):
        pass

    def _resolve_wildcard(self, file):
        return None

@pytest.fixture
def parameters():
    return dict(
        EXECUTION_TIME='19000101'
    )
