""" Oneview PPD Transformer"""
from   io import BytesIO

import logging
import pandas

from   datalabs.etl.oneview.iqvia.column import BUSINESS_COLUMNS, PROVIDER_COLUMNS, PROVIDER_AFFILIATION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIATransformerTask(TransformerTask):
    def _to_dataframe(self):
        iqvia_data = [pandas.read_csv(BytesIO(csv)) for csv in self._parameters['data']]
        provider_affiliation_data = iqvia_data[2]

        primary_keys = [str(column['IMS_ORG_ID']) + str(column['PROFESSIONAL_ID'])
                        for index, column in provider_affiliation_data.iterrows()]
        provider_affiliation_data['id'] = primary_keys

        return [iqvia_data[0], iqvia_data[1], provider_affiliation_data]

    def _get_columns(self):
        return [BUSINESS_COLUMNS, PROVIDER_COLUMNS, PROVIDER_AFFILIATION_COLUMNS]
