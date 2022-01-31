"""Task for DAG status notifications"""
import json
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
        message = 'The {} DAG run at {} UTC in the {} environment has status {}.'.format(
            dag,
            execution_time,
            self.environment,
            status.name
        )
        subject = '[DAG STATUS] {} {} {}'.format(self.environment, dag, status.name)

        send_email(self.emails, subject, body=message, from_account=self.from_account)
        LOGGER.info('EMAIL SENT TO {}'.format(self.emails))
