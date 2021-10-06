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

        historical_resident['id'] = \
            historical_resident.medical_education_number.astype(str) + historical_resident.start_year.astype(str)

        return data

    def _get_columns(self):
        return [column.HISTORICAL_RESIDENCY]
