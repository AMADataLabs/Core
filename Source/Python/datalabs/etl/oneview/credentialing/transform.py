"""Oneview Credentialing Table Columns"""

import logging
import os
import pandas

from   datalabs.etl.task import ETLException
from   datalabs.etl.oneview.credentialing.column import customer_columns, product_columns, order_columns
from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CredentialingTransformer(TransformerTask):
    def _get_columns(self):
        return [customer_columns, product_columns, order_columns]
