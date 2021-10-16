""" Archival Transformer classes. """
from   io import BytesIO
import pickle
from   zipfile import ZipFile

from datalabs.etl.transform import TransformerTask


class ZipTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        zip_data = BytesIO()
        filename_data_tuples = pickle.loads(self._parameters['data'][0])
        LOGGER.debug(f'Data to zip: {filename_data_tuples}')

        with ZipFile(zip_data, 'w') as zip_file:
            for file, data in filename_data_tuples:
                zip_file.writestr(file, data)

        return [bytes(zip_data.getbuffer())]
