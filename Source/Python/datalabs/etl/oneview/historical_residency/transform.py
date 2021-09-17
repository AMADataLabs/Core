""" Oneview Historical Residency Transformer"""
import logging

from   datalabs.etl.oneview.historical_residency import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HistoricalResidencyTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, path, on_disk, **kwargs):
        return super()._csv_to_dataframe(path, on_disk, sep='|')

    def _get_columns(self):
        return [column.HISTORICAL_RESIDENCY]
