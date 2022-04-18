""" Archival Transformer classes. """
from   io import BytesIO
from   dataclasses import dataclass
import logging
import pickle
from   zipfile import ZipFile

from datalabs.etl.transform import TransformerTask
from datalabs.etl.extract import FileExtractorTask, IncludeNamesMixin
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class UnzipTransformerParameters:
    data: object
    files: str = None
    include_names: str = None
    include_datestamp: str = None
    execution_time: str = None

class ZipTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        zip_data = BytesIO()
        filename_data_tuples = pickle.loads(self._parameters['data'][0])

        with ZipFile(zip_data, 'w') as zip_file:
            for file, data in filename_data_tuples:
                LOGGER.debug('Adding %s byte file %s to the archive...', len(data), file)
                zip_file.writestr(file, data)

        return [bytes(zip_data.getbuffer())]


class UnzipTransformerTask(IncludeNamesMixin, FileExtractorTask):
    PARAMETER_CLASS = UnzipTransformerParameters

    def _get_client(self) -> 'Context Manager':
        return ZipFile(BytesIO(self._parameters.data[0]))

    def _get_files(self) -> list:
        return self._client.namelist()

    def _extract_file(self, file):
        return self._client.read(file)

    def _resolve_wildcard(self, file):
        return [file]
