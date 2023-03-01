"""Expanded PPD extractor"""
from datalabs.etl.fs.extract import LocalFileExtractorTask
from datalabs.etl.sftp.extract import SFTPFileExtractorTask


def _filter_for_latest_file(candidate_files):
    return sorted(candidate_files)[-1]


# pylint: disable=too-many-ancestors
class LocalPPDExtractorTask(LocalFileExtractorTask):
    def _extract_files(self, files):
        latest_file = _filter_for_latest_file(files)

        return super()._extract_files([latest_file])


# pylint: disable=too-many-ancestors
class UDrivePPDExtractorTask(SFTPFileExtractorTask):
    def _extract_files(self, files):
        latest_file = _filter_for_latest_file(files)

        return super()._extract_files([latest_file])
