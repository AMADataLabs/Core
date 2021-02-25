"""Expanded PPD extractor"""
from datalabs.etl.fs.extract import LocalUnicodeTextFileExtractorTask


# pylint: disable=too-many-ancestors
class LocalPPDExtractorTask(LocalUnicodeTextFileExtractorTask):
    def _extract_files(self, files):
        latest_file = self._filter_for_latest_file(files)

        return super()._extract_files([latest_file])

    @classmethod
    def _filter_for_latest_file(cls, candidate_files):
        return sorted(candidate_files)[-1]
