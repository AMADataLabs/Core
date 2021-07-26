''' Class for notifying tasks to run via SNS. '''
import json
import logging

from   datalabs.access.aws import AWSClient
from   datalabs.parameter import ParameterValidatorMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class SNSTaskNotifier(ParameterValidatorMixin):
    def __init__(self, task_topic_arn: str):
        self._task_topic_arn = task_topic_arn

    def notify(self, dag, task, execution_time):
        message = json.dumps(dict(
            dag=dag,
            task=task,
            execution_time=execution_time
        ))

        with AWSClient("sns") as sns:
            sns.publish(
                TargetArn=self._task_topic_arn,
                Message=message
            )
