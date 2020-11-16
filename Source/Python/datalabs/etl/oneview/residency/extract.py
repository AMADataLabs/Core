""" Oneview Residency Extractor """

import pandas

from   datalabs.etl.sftp.extract import SFTPUnicodeTextFileExtractorTask


class ResidencyExtractor(SFTPUnicodeTextFileExtractorTask):
    def _extract(self):
        residency_data = super()._extract()

        return [self._to_dataframe(data) for data in residency_data]

    def _to_dataframe(self, file):
        dataframe = pandas.read_csv(file, sep='|', error_bad_lines=False, encoding='latin', low_memory=False)
        return dataframe
