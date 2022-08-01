"""Task for DAG status notifications"""
import logging

from   datalabs.messaging.email_message import send_email

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class StatusEmailNotifier():
    def __init__(self, emails, environment, from_account):
        self.emails = emails
        self.environment = environment
        self.from_account = from_account

    def notify(self, dag, execution_time, status):
        message = f'The {dag} DAG run at {execution_time} UTC in the {self.environment} '\
                  f'environment has status {status.value}.'
        subject = f'[DAG STATUS] {self.environment} {dag} {status.value}'

        send_email(self.emails, subject, body=message, from_account=self.from_account)
        LOGGER.info('WEB HOOK url2')
        LOGGER.info('EMAIL SENT TO %s', self.emails)
