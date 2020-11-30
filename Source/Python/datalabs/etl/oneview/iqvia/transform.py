""" Oneview PPD Transformer"""
import logging

from   datalabs.etl.oneview.iqvia.column import BUSINESS_COLUMNS, PROVIDER_COLUMNS, PROVIDER_AFFILIATION_COLUMNS
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIATransformer(TransformerTask):
    def _get_columns(self):
        return [BUSINESS_COLUMNS, PROVIDER_COLUMNS, PROVIDER_AFFILIATION_COLUMNS]
