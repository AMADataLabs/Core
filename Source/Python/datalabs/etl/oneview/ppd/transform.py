""" Oneview PPD Transformer"""
import logging
import datalabs.etl.oneview.columns as columns

from datalabs.etl.transform import TransformerTask
from datalabs.etl.task import ETLException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDDataFramesToCSVText(TransformerTask):
    def _transform(self):
        LOGGER.debug('Data to transform: %s', self._parameters.data)

        try:
            updated_df = [self._update_column_names(data) for data in self._parameters.data]
            updated_csv = [self._dataframe_to_csv(data) for data in updated_df]

        except Exception as exception:
            raise ETLException("Invalid data") from exception

        return updated_csv

    @classmethod
    def _update_column_names(cls, data):
        data.columns = columns
        return data

    @classmethod
    def _dataframe_to_csv(cls, data):
        csv = data.to_csv(index=False)
        return csv
