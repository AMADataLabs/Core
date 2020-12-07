""" Oneview RaceEthnicity Transformer"""
import logging

from   datalabs.etl.oneview.race_ethnicity.column import race_ethnicity_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class RaceEthnicityTransformerTask(TransformerTask):
    def _transform(self):
        self._parameters.data = [self._to_dataframe(data) for data in self._parameters.data]
        race_ethnicity_data = super()._transform()

        return race_ethnicity_data

    def _get_columns(self):
        return [race_ethnicity_columns]