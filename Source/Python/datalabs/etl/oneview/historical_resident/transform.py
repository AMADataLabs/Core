""" Oneview Historical Residency Transformer"""
import logging

from   datalabs.etl.oneview.historical_resident import column
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HistoricalResidentTransformerTask(TransformerTask):
    @classmethod
    def _csv_to_dataframe(cls, data, **kwargs):
        return super()._csv_to_dataframe(data, sep='|')

    def _postprocess(self, dataset):
        historical_resident = dataset[0]

        historical_resident['id'] = \
            historical_resident.medical_education_number.astype(str) +'-' \
            + historical_resident.specialty.astype(str) + '-' \
            + historical_resident.institution_code.astype(str) + '-' \
            + historical_resident.start_year.astype(str)

        return [historical_resident]

    def _get_columns(self):
        return [column.HISTORICAL_RESIDENCY]


class HistoricalResidentPruningTransformerTask(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        historical_residents, physicians = dataset

        historical_residents = historical_residents[
            historical_residents.medical_education_number.isin(physicians.medical_education_number)
        ]

        return [historical_residents]

    def _get_columns(self):
        columns = {value:value for value in column.HISTORICAL_RESIDENCY.values()}

        columns['id'] = 'id'

        return [columns]
