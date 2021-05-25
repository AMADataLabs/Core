""" Oneview Melissa Transformer"""
import logging

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.melissa.column as columns

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class MelissaTransformerTask(TransformerTask):
    def _get_columns(self):
        return [
            columns.ZIP_CODE_COLUMNS,
            columns.COUNTY_COLUMNS,
            columns.AREA_CODE_COLUMNS,
            columns.CENSUS_COLUMNS,
            columns.CORE_BASED_STATISTICAL_AREA_COLUMNS,
            columns.ZIP_CODE_CORE_BASED_STATISTICAL_AREA_COLUMNS,
            columns.METROPOLITAN_STATISTICAL_AREA_COLUMNS
        ]
