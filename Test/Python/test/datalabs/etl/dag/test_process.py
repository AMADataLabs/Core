""" Source: datalabs.etl.dag.process """
import os

import pytest

from   datalabs.etl.dag.state.file import DAGState, TaskState
from   datalabs.etl.dag.process import DAGProcessorTask, TaskProcessorTask


# pylint: disable=redefined-outer-name
def test_dag_processor_runs(dag_parameters):
    dag_processor = DAGProcessorTask(dag_parameters)

    dag_processor.run()


# pylint: disable=redefined-outer-name
def test_task_processor_runs(task_parameters):
    task_processor = TaskProcessorTask(task_parameters)

    task_processor.run()


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
        STATE_CLASS=DAGState,
        DAG_CLASS=TestDAG,
        EXECUTION_TIME="2021-01-21T12:24:38+00.00"
    )


@pytest.fixture
def task_parameters():
    return dict(
        DAG="TestDAG",
        TASK="TestTask",
        DAG_CLASS=TestDAG,
        STATE_CLASS=TaskState,
        EXECUTION_TIME="2021-01-21T12:24:38+00.00",
    )


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['DAG_CLASS'] = 'test.datalabs.etl.dag.test_resolve.TestDAG'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
