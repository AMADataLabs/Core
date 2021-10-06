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

    @classmethod
    def _postprocess_data(cls, data):
        historical_resident = data[0]

        historical_resident['id'] = data.medical_education_number.astype(str) + data.start_year.astype(str)

        return data

        return historical_resident

    def _get_columns(self):
        return [column.HISTORICAL_RESIDENCY]
