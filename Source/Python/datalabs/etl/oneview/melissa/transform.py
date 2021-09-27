""" Oneview Melissa Transformer"""
import logging

import datalabs.etl.oneview.melissa.column as columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class MelissaTransformerTask(TransformerTask):
    def _preprocess_data(self, data):
        zip_code_data, county_data, area_code_data, census_data, cbsa_data, zip_code_cbsa_data, msa_data = data

        zip_codes = self._generate_zip_code_primary_keys(zip_code_data)
        zip_codes['FIPS_CD'] = zip_codes['FIPS_CD'].str.lstrip('0')

        area_codes = self._generate_area_code_primary_keys(area_code_data)

        return [zip_codes, county_data, area_codes, census_data, cbsa_data, zip_code_cbsa_data, msa_data]

    @classmethod
    def _generate_zip_code_primary_keys(cls, data):
        data['id'] = data['ZIP'].astype(str) + data['CITY_CD'].astype(str)

        return data

    @classmethod
    def _generate_area_code_primary_keys(cls, data):
        data['id'] = data['AREA_CD'].astype(str) + data['PREFIX'].astype(str)

        return data.drop_duplicates(subset=['id'], ignore_index=True)

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
