""" OneView Reference Transformer"""
import logging
import pandas

from   io import StringIO

from   datalabs.etl.oneview.reference.column import MPA_COLUMNS, TOP_COLUMNS, PE_COLUMNS, CBSA_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class MajorProfessionalActivityTransformerTask(TransformerTask):
    def _get_columns(self):
        return [MPA_COLUMNS]


class TypeOfPracticeTransformerTask(TransformerTask):
    def _get_columns(self):
        return [TOP_COLUMNS]


class PresentEmploymentTransformerTask(TransformerTask):
    def _get_columns(self):
        return [PE_COLUMNS]


class CoreBasedStatisticalAreaTransformerTask(TransformerTask):
    def _transform(self):
        self._parameters.data = self._to_dataframe()
        core_based_statistical_area_data = super()._transform()

        return core_based_statistical_area_data

    def _to_dataframe(self):
        return [pandas.read_csv(StringIO(file)) for file in self._parameters.data]

    def _get_columns(self):
        return [CBSA_COLUMNS]
