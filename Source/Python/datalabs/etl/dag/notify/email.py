"""Task for DAG status notifications"""
import json
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.messaging.email_message import send_email

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class StatusEmailNotifier():
    def __init__(self, dag_topic_arn: str, emails):
        self._dag_topic_arn = dag_topic_arn
        self.emails = emails

    def notify(self, dag, execution_time):
        message = json.dumps(dict(
            dag=dag,
            execution_time=execution_time
        ))

        with AWSClient("sns") as sns:
            sns.publish(
                TargetArn=self._dag_topic_arn,
                Message=message
            )

        send_email(self.emails, 'Dag Notification', body=message)
