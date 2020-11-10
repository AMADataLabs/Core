""" Oneview PPD Transformer"""
import logging

from   datalabs.etl.oneview.iqvia.column import business_columns, provider_columns, provider_affiliation_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class IQVIATransformer(TransformerTask):
    def _get_columns(self):
        return [business_columns, provider_columns, provider_affiliation_columns]
