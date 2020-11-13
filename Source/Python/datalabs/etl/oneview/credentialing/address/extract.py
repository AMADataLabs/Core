""" Oneview credentialing addresses extractor """

import logging

from   datalabs.etl.sftp.extract import SFTPUnicodeTextFileExtractorTask


class CredentialingAddressesExtractor(SFTPUnicodeTextFileExtractorTask):
    def _extract(self):
        with self._get_sftp(self._parameters.variables) as sftp:
            file_paths = self._get_file_paths(sftp)
            logging.info('Extracting the following files via SFTP: %s', file_paths)

            data = [self._extract_file(sftp, file) for file in file_paths]

        return data
