""" Transformer Class for hcpcs """
import fnmatch

from   datalabs.etl.archive.transform import UnzipTransformerTask


# pylint: disable=too-many-ancestors
class HCPCSUnzipTransformerTask(UnzipTransformerTask):
    @property
    def include_names(self):
        return False

    def _get_files(self):
        xlsx_files = fnmatch.filter(self._client.files, "*.xlsx")
        largest_file = xlsx_files[0]

        for file in xlsx_files:
            if self._client.get_info(file) > self._client.get_info(largest_file):
                largest_file = file

        return [largest_file]
