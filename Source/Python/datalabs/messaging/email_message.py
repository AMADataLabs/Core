""" Sends an email using AMA SMTP configuration """
import os
import smtplib
from email.message import EmailMessage


# pylint: disable=too-many-arguments, invalid-name
def send_email(to, subject, cc=None, body=None, attachments=None, from_account=None, html_content=None):
    with smtplib.SMTP('amamx.ama-assn.org') as smtp:
        msg = EmailMessage()
        msg['To'] = to
        if 'cc' is not None:
            msg['Cc'] = cc
        msg['Subject'] = subject
        if body is not None:
            msg.set_content(body)
        if html_content is not None:
            msg.add_alternative(f"{html_content}", subtype='html')
        if attachments is not None:
            if isinstance(attachments, str):
                attachments = {attachments}
            if not hasattr(attachments, '__iter__'):
                raise ValueError('attachments parameter must be an iterable')
            attachments = set(attachments)  # do not attach same file multiple times
            for attachment in attachments:
                if not os.path.exists(attachment):
                    raise FileNotFoundError(f'File path {attachment} not found.')
                with open(attachment, 'rb') as f:
                    data = f.read()
                attachment = attachment.replace('\\', '/')
                msg.add_attachment(
                    data,
                    filename=attachment.split('/')[-1],
                    maintype='application',
                    subtype='octet-stream'
                )

        if from_account is None:
            from_account = os.environ.get('AMA_EMAIL_ADDRESS')
            if from_account is None:
                raise EnvironmentError('from_account parameter not specified and environment variable '
                                       'not set - cannot determine email address to send email message from.')
        msg['From'] = from_account

        smtp.send_message(msg)
