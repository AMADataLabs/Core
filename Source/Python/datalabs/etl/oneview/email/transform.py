""" Oneview Email Transformer"""
import logging

from   datalabs.etl.oneview.email.column import EMAIL_COLUMNS

from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PhysicianEmailStatusTransformer(TransformerTask):
    def _preprocess_data(self, data):
        email_status = data[0]

        email_status['has_email'] = email_status.EMAIL_STATUS == 'valid'

        return [email_status]

    def _get_columns(self):
        return [EMAIL_COLUMNS]
