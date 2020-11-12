""" Oneview Residency Extractor """

import pandas

from   datalabs.etl.fs.extract import LocalUnicodeTextFileExtractorTask


class ResidencyExtractor(LocalUnicodeTextFileExtractorTask):
    def _extract(self):
        residency_files = super()._get_files()

        return [self._to_dataframe(file) for file in residency_files]

    def _to_dataframe(self, file):
        dataframe = pandas.read_csv(file, sep='|', error_bad_lines=False, encoding='latin', low_memory=False)
        return dataframe
