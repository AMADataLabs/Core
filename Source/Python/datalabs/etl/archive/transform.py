""" Archival Transformer classes. """
from   io import BytesIO
import logging
import pickle
from   zipfile import ZipFile

from datalabs.etl.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ZipTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        zip_data = BytesIO()
        filename_data_tuples = pickle.loads(self._parameters['data'][0])

        with ZipFile(zip_data, 'w') as zip_file:
            for file, data in filename_data_tuples:
                LOGGER.debug(f'Adding {len(data)} byte file {file} to the archive...')
                zip_file.writestr(file, data)

        return [bytes(zip_data.getbuffer())]
