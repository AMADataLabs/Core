""" Oneview Melissa Transformer"""
import logging

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.melissa.column as columns

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class MelissaTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        zip_code_data = data[0]

        primary_keys = [str(column['ZIP']) + str(column['CITY_CD'])
                        for index, column in zip_code_data.iterrows()]
        zip_code_data['id'] = primary_keys

        return [zip_code_data, data[1], data[2], data[3], data[4], data[5], data[6]]

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
