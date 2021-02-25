""" Archival Transformer classes. """
from io import BytesIO
from zipfile import ZipFile

from datalabs.etl.transform import TransformerTask


class ZipTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        zip_data = BytesIO()

        with ZipFile(zip_data, 'w') as zip_file:
            for file, data in self._parameters['data']:
                zip_file.writestr(file, data)

        return [bytes(zip_data.getbuffer())]
