"""Task for DAG status notifications"""
import json
import logging

from   datalabs.messaging.email_message import send_email

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class StatusEmailNotifier():
    def __init__(self, emails, environment):
        self.emails = emails
        self.environment = environment

    def notify(self, dag, execution_time, status):
        message = 'The {} DAG run at {} UTC in the {} environment has {}.'.format(dag, execution_time,
                                                                                  self.environment, status)
        subject = '[DAG Status] {} {} {}'.format(self.environment, dag, status)

        send_email(self.emails, subject, body=message)
        LOGGER.info('EMAIL SENT TO {}'.format(self.emails))
