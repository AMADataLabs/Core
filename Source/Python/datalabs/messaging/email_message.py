""" Sends an email using AMA SMTP configuration """
import logging
import os
import smtplib
from   email.message import EmailMessage # pylint: disable=no-name-in-module, import-error

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
logging.basicConfig()


class Attachment:
    def __init__(self, name=None, file_path=None, data=None):
        """
        :param name: string - name of attachment file as it appears in the email
        :param file_path: string - absolute or relative path to file to add as attachment
        :param data: Bytes of data for the attachment, will be overridden by file_path file if file_path not None
        """
        self.name = name
        self.data: bytes = data

        if file_path is not None:
            if not os.path.exists(file_path):
                raise FileNotFoundError(file_path)
            with open(file_path, 'rb') as file:
                self.data = file.read()
            # if name is None, determine filename automatically from file path
            if self.name in [None, '', '/']:
                self.name = file_path.replace('\\', '/').split('/')[-1]

        if self.data is None:
            raise ValueError("Data is None")

        if self.name is None:
            raise ValueError("Name is None")


# pylint: disable=too-many-arguments, invalid-name
def send_email(to, subject, cc=None, body=None, attachments: [Attachment] = None, from_account=None, html_content=None):
    """
    :param to: string of ';' delimited email addresses or list of email addresses
    :param subject: string
    :param cc: string of ';' delimited email addresses or list of email addresses
    :param body: string
    :param attachments: list of Attachment objects (see above)
    :param from_account: string of account to send email from
    :param html_content: html data to insert
    :return: None
    """

    message = create_message(to, subject, cc, body, attachments, from_account, html_content)

    with smtplib.SMTP('amamx.ama-assn.org') as smtp:
        LOGGER.info('SMTP CONNECTION SUCCESSFUL')

        smtp.send_message(message)


# pylint: disable=too-many-arguments, invalid-name, line-too-long
def create_message(to, subject, cc=None, body=None, attachments: [Attachment] = None, from_account=None, html_content=None) -> EmailMessage:
    message = EmailMessage()
    message['To'] = to

    if cc not in [None, '']:
        message['Cc'] = cc
    message['Subject'] = subject

    if body is not None:
        message.set_content(body)

    if html_content is not None:
        message.add_alternative(f"{html_content}", subtype='html')

    if attachments is not None:
        for attachment in set(attachments):
            LOGGER.debug(
                'Attachment "%s" data of type %s:\n%s',
                attachment.name,
                type(attachment.data),
                attachment.data
            )
            message.add_attachment(
                attachment.data,
                filename=attachment.name,
                maintype='application',
                subtype='octet-stream'
            )

    if from_account is None:
        from_account = os.environ.get('AMA_EMAIL_ADDRESS')
        if from_account is None:
            raise EnvironmentError('from_account parameter not specified and environment variable '
                                   'not set - cannot determine email address to send email message from.')
    message['From'] = from_account

    return message
