""" Oneview PPD Transformer"""
import logging

from   datalabs.etl.oneview.ppd.columns import names
from   datalabs.etl.oneview.ppd.columns import columns

from datalabs.etl.oneview.column import UpdateColumns
from datalabs.etl.transform import TransformerTask
from datalabs.etl.task import ETLException

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDDataFramesToCSVText(TransformerTask):
    def _transform(self):
        LOGGER.debug('Data to transform: %s', self._parameters.data)

        try:
            updated_df = UpdateColumns.change_names(self._parameters.data, names, columns)
            updated_csv = self._dataframe_to_csv(updated_df)

        except Exception as exception:
            raise ETLException("Invalid data") from exception

        return updated_csv

    @classmethod
    def _dataframe_to_csv(cls, data):
        csv = data.to_csv(index=False)
        return csv
