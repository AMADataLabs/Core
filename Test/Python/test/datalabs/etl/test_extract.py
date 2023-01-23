""" source: datalabs.etl.extract """
import pytest

from   datetime import datetime, timedelta

from   datalabs.etl.extract import FileExtractorTask, TargetOffsetMixin


def test_default_get_target_datetime(file_extractor, parameters):
    date = file_extractor._get_target_datetime()

    assert date == parameters.get('EXECUTION_TIME')


def test_resolve_timestamps(file_extractor):
    file_names = ["testfile1 - %Y-%m-%d.xlsx", "testfile2 - %Y-%m-%d.xlsx", "testfile3 - %Y-%m-%d.xlsx"]

    file_extractor._target_datetime = datetime(2023, 1, 18, 3, 55)
    files = file_extractor._resolve_timestamps(file_names)

    assert files == ["testfile1 - 2023-01-18.xlsx", "testfile2 - 2023-01-18.xlsx", "testfile3 - 2023-01-18.xlsx"]


def test_target_offset_mixin(mixin_parent_class, parameters):
    date = mixin_parent_class._get_target_datetime()
    actual_date = parameters.get('EXECUTION_TIME') - timedelta(weeks=1)

    assert date == actual_date


@pytest.fixture
def mixin_parent_class(parameters):
    return MixinParentClass(parameters, [b'True'])


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


class MixinParentClass(TargetOffsetMixin, FileExtractorTask):
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
        EXECUTION_OFFSET='{"weeks": 1}',
        EXECUTION_TIME=datetime.utcnow().replace(second=0, microsecond=0)
    )
