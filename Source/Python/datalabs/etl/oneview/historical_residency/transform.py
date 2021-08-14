""" Oneview Historical Residency Transformer"""
from   io import BytesIO

import logging
import pandas

from   datalabs.etl.oneview.historical_residency import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HistoricalResidencyTransformerTask(TransformerTask):
    def _csv_to_dataframe(cls, data):
        return [pandas.read_csv(BytesIO(file), sep='|') for file in data]

    def _get_columns(self):
        return [column.HISTORICAL_RESIDENCY]
