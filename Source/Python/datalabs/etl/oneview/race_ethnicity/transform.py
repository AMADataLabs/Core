""" Oneview RaceEthnicity Transformer"""
from   io import StringIO
import logging

import pandas

from   datalabs.etl.oneview.race_ethnicity.column import RACE_ETHNICITY_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class RaceEthnicityTransformerTask(TransformerTask):
    def _transform(self):
        self._parameters.data = [self._to_dataframe(data) for data in self._parameters.data]
        race_ethnicity_data = super()._transform()

        return race_ethnicity_data

    @classmethod
    def _to_dataframe(cls, file):
        dataframe = pandas.read_csv(StringIO(file))
        return dataframe

    def _get_columns(self):
        return [RACE_ETHNICITY_COLUMNS]
