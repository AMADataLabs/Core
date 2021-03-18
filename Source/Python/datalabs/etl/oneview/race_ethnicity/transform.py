""" Oneview RaceEthnicity Transformer"""
from   io import BytesIO
import logging

import pandas

from   datalabs.etl.oneview.race_ethnicity.column import RACE_ETHNICITY_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class RaceEthnicityTransformerTask(TransformerTask):
    def _get_columns(self):
        return [RACE_ETHNICITY_COLUMNS]
