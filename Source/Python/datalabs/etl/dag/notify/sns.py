''' Class for notifying tasks to run via SNS. '''
import json
import logging

from   datalabs.access.aws import AWSClient

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)



class SNSDAGNotifier():
    def __init__(self, dag_topic_arn: str):
        self._dag_topic_arn = dag_topic_arn

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


class SNSTaskNotifier():
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
