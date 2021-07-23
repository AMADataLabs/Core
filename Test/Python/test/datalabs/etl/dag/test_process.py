""" Source: datalabs.etl.dag.process """
import json
import os

import pytest

from   datalabs.access.aws import AWSClient
from   datalabs.etl.dag.process import DAGProcessorTask, TaskProcessorTask


# pylint: disable=redefined-outer-name
def test_dag_processor_runs(dag_parameters):
    dag_processor = DAGProcessorTask(dag_parameters)

    dag_processor.run()


# pylint: disable=redefined-outer-name
def test_task_processor_runs(task_parameters):
    task_processor = TaskProcessorTask(task_parameters)

    task_processor.run()


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_trigger_dag_processor_via_sns():
    message = json.dumps(dict(
        dag="DAG_SCHEDULER",
        execution_time="2021-01-21T12:24:38.452349885"
    ))

    with AWSClient("sns") as sns:
        sns.publish(
            TargetArn="arn:aws:sns:us-east-1:644454719059:DataLake-DAG-Processor-sbx",
            Message=message
        )


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_trigger_task_processor_via_sns():
    message = json.dumps(dict(
        dag="DAG_SCHEDULER",
        task="EXTRACT_SCHEDULE",
        execution_time="2021-01-21T12:24:38.452349885"
    ))

    with AWSClient("sns") as sns:
        sns.publish(
            TargetArn="arn:aws:sns:us-east-1:644454719059:DataLake-Task-Processor-sbx",
            Message=message
        )

class TestDAG:
    # pylint: disable=unused-argument
    @classmethod
    def task_class(cls, name):
        return TestTask


class TestTask:
    pass


@pytest.fixture
def dag_parameters():
    return dict(
        DAG="TestDAG",
        DAG_CLASS=TestDAG,
        DAG_STATE_CLASS='datalabs.etl.dag.state.file.DAGState',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.local.LocalDAGExecutor',
        EXECUTION_TIME="2021-01-21T12:24:38+00.00"
    )


@pytest.fixture
def task_parameters():
    return dict(
        DAG="TestDAG",
        TASK="TestTask",
        DAG_CLASS=TestDAG,
        DAG_STATE_CLASS='datalabs.etl.dag.state.file.DAGState',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.local.LocalDAGExecutor',
        EXECUTION_TIME="2021-01-21T12:24:38+00.00",
    )


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['DAG_CLASS'] = 'test.datalabs.etl.dag.test_resolve.TestDAG'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
