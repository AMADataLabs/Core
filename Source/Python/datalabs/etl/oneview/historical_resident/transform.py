""" Oneview Historical Residency Transformer"""
import logging

from   datalabs.etl.oneview.historical_resident import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HistoricalResidentTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, data, on_disk, **kwargs):
        return super()._csv_to_dataframe(data, on_disk, sep='|')

    def _preprocess_data(self, data):
        historical_resident = data[0]

        primary_keys = list(range(len(historical_resident)))

        historical_resident['id'] = primary_keys

    def _get_columns(self):
        return [column.HISTORICAL_RESIDENCY]
