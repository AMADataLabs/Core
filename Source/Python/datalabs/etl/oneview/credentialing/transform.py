"""Oneview Credentialing Table Columns"""
import logging

from datalabs.etl.oneview.credentialing.column import CUSTOMER_COLUMNS, PRODUCT_COLUMNS, ORDER_COLUMNS
from datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformer(TransformerTask):
    def _get_columns(self):
        return [CUSTOMER_COLUMNS, PRODUCT_COLUMNS, ORDER_COLUMNS]
