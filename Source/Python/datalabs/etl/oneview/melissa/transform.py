""" Oneview Melissa Transformer"""
import logging
import dask.array

from   datalabs.etl.oneview.transform import TransformerTask

import datalabs.etl.oneview.melissa.column as columns

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class MelissaTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        zip_code_data = data[0]
        area_code_data = data[2]

        zip_codes = self._generate_zip_code_primary_keys(zip_code_data)
        zip_codes['FIPS_CD'] = zip_codes['FIPS_CD'].str.lstrip('0')

        area_codes = self._generate_area_code_primary_keys(area_code_data)

        return [zip_codes, data[1], area_codes, data[3], data[4], data[5], data[6]]

    @classmethod
    def _generate_zip_code_primary_keys(cls, data):
        zip_code_primary_keys = dask.array.array([str(column['ZIP']) + str(column['CITY_CD'])
                                                  for index, column in data.iterrows()])
        data['id'] = zip_code_primary_keys

        return data

    @classmethod
    def _generate_area_code_primary_keys(cls, data):
        area_code_primary_keys = dask.array.array([str(column['AREA_CD']) + str(column['PREFIX'])
                                                   for index, column in data.iterrows()])
        data['id'] = area_code_primary_keys

        return data

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
