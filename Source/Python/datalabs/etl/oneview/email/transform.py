""" Oneview Email Transformer"""
import logging

from   datalabs.etl.oneview.email.column import EMAIL_COLUMNS

from   datalabs.etl.oneview.transform import TransformerTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PhysicianEmailTransformer(TransformerTask):
    def _preprocess_data(self, data):
        email_address, email_id = data

        emails = email_address.merge(email_address, how="inner", on='EMAIL_ID')
        emails = self._add_flag(emails)

        return [emails]

    @classmethod
    def _add_flag(cls, emails):
        emails['has_email'] = ''

        for row in emails:
            if row.EMAIL_STATUS == 'valid':
                row.has_email = True
            else:
                row.has_email = False

        return emails

    def _get_columns(self):
        return [EMAIL_COLUMNS]
