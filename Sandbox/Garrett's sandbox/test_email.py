""" Just some examples around send_email and Attachments """

from io import BytesIO
from datalabs.messaging.email_message import send_email, Attachment


def test_manual_attachment_email():
    """ Attachment option 1 - specify path to a local file """
    a = Attachment(file_path='test_email/dog.jpg')

    """ Attachment option 2 - specify attachment name and data directly """
    with open('test_email/test_attachment.txt', 'rb') as f:
        a2 = Attachment(
            name='test_att.txt',
            data=f
        )

        send_email(
            to='garrett.lappe@ama-assn.org',
            from_account='garrett.lappe@ama-assn.org',
            subject='test',
            attachments=[a, a2]
        )


""" EXAMPLE EMAIL LOADER TASK"""

from dataclasses import dataclass
from datalabs.parameter import add_schema
from datalabs.etl.load import LoaderTask

@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SomeEmailLoaderParameters:
    to: str or [str]
    cc: str or [str]
    data = None

class SomeEmailLoader(LoaderTask):
    PARAMETER_CLASS = SomeEmailLoaderParameters
    def _load(self):
        attachment = Attachment(name='test.jpg', data=self._parameters.data[0])
        send_email(
            to=self._parameters.to,
            cc=self._parameters.cc,
            attachments=[attachment],
            from_account='datalabs@ama-assn.org',
            subject='Test from email loader'
        )


def test_loader():
    with open(
            'test_email/dog.jpg',
            'rb'
    ) as f:
        loader = SomeEmailLoader(
            parameters={
                'to': '<your_email_address_here>',
                'cc': '',
                'data': [f]
            }
        )
        loader._load()
