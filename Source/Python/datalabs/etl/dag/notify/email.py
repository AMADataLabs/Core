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

    def notify(self, dag, execution_time):
        message = json.dumps(dict(
            dag=dag,
            execution_time=execution_time
        ))

        send_email(self.emails, 'Dag Notification', body=message)
