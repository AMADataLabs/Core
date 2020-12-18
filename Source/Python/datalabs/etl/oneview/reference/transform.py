""" OneView Reference Transformer"""
import logging
import pandas

from   io import StringIO

from   datalabs.etl.oneview.reference.column import MPA_COLUMNS, TOP_COLUMNS, PE_COLUMNS, CBSA_COLUMNS, SPECIALTY_COLUMNS
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

    @classmethod
    def _to_dataframe(cls):
        return [pandas.read_csv(StringIO(file)) for file in cls._parameters.data]

    def _get_columns(self):
        return [CBSA_COLUMNS]


class SpecialtyTransformerTask(TransformerTask):
    def _get_columns(self):
        return [SPECIALTY_COLUMNS]


class SpecialtyMergeTransformerTask(TransformerTask):
    def _transform(self):
        csv_to_df = [self._dataframe_to_csv(csv) for csv in self._parameters.data]
        filtered_dataframe = csv_to_df[0].loc[csv_to_df[0].id.isin(csv_to_df[1].primary_specialty) |
                                        csv_to_df[0].id.isin(csv_to_df[1].secondary_specialty)].reset_index(drop=True)

        self._parameters.data = filtered_dataframe

        return super()._transform()

    @classmethod
    def _to_dataframe(cls, file):
        return pandas.read_csv(StringIO(file))
