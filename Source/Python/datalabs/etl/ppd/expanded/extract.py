from datalabs.etl.fs.extract import LocalUnicodeTextFileExtractorTask


class LocalPPDExtractorTask(LocalUnicodeTextFileExtractorTask):
    def _extract(self):
        candidate_files = super()._get_files()
        latest_file = self._filter_for_latest_file(candidate_files)

        return [(latest_file, self._extract_file(latest_file))]

    def _filter_for_latest_file(self, candidate_files):
        return sorted(candidate_files)[-1]
