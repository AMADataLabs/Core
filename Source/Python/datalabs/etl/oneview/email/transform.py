""" Oneview Email Transformer"""
import logging

from   datalabs.etl.oneview.email.column import EMAIL_COLUMNS

from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PhysicianEmailStatusTransformer(TransformerTask):
    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        email_status = dataset[0]

        email_status.sort_values('EMAIL_STATUS')
        email_status.drop_duplicates('PARTY_ID', keep='last', inplace=True)

        email_status['has_email'] = email_status.EMAIL_STATUS == 'valid'

        return [email_status]

    def _get_columns(self):
        return [EMAIL_COLUMNS]
