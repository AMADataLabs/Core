""" Oneview Melissa Transformer"""
import logging

from   datalabs.etl.oneview.melissa.column import ZIP_CODE_COLUMNS, COUNTY_COLUMNS, AREA_CODE_COLUMNS, CENSUS_COLUMNS, \
    CORE_BASED_STATISTICAL_AREA_COLUMNS, ZIP_CODE_CORE_BASED_STATISTICAL_AREA_COLUMNS, \
    METROPOLITAN_STATISTICAL_AREA_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class MelissaTransformerTask(TransformerTask):
    def _get_columns(self):
        return [ZIP_CODE_COLUMNS, COUNTY_COLUMNS, AREA_CODE_COLUMNS, CENSUS_COLUMNS,
                CORE_BASED_STATISTICAL_AREA_COLUMNS, ZIP_CODE_CORE_BASED_STATISTICAL_AREA_COLUMNS,
                METROPOLITAN_STATISTICAL_AREA_COLUMNS]
