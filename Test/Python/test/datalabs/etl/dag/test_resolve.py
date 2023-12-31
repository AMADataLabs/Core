""" Source: datalabs.etl.dag.resolve """
import os

import pytest

from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.dag.resolve import TaskResolver


# pylint: disable=redefined-outer-name
def test_task_resolver_gets_dag_executor(dag_parameters):
    os.environ["DAG_CLASS"] = 'datalabs.etl.dag.schedule.dag.DAGSchedulerDAG'
    task_class = TaskResolver.get_task_class(dag_parameters)

    assert task_class.__qualname__ == 'LocalDAGExecutorTask'


# pylint: disable=redefined-outer-name, unused-argument
def test_task_resolver_gets_dag_task(environment, task_parameters):
    task_class = TaskResolver.get_task_class(task_parameters)

    assert task_class.__qualname__ == 'TestTask'


# pylint: disable=redefined-outer-name
def test_invalid_dag_plugin_event_type(bad_type_parameters):
    with pytest.raises(ValueError):
        TaskResolver.get_task_class(bad_type_parameters)


class TestDAG(DAG):
    TEST_TASK: "test.datalabs.etl.dag.test_resolve.TestTask"


class TestTask:
    pass


@pytest.fixture
def dag_parameters():
    return dict(
        type="DAG",
        execution_time="2021-01-21T12:24:38+00.00",
        dag_class='test.datalabs.etl.dag.test_resolve.TestDAG'
    )


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['DAG_CLASS'] = 'test.datalabs.etl.dag.test_resolve.TestDAG'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)


@pytest.fixture
def task_parameters():
    return dict(
        type="Task",
        execution_time="2021-01-21T12:24:38+00.00",
        task="TEST_TASK",
        dag_class='test.datalabs.etl.dag.test_resolve.TestDAG'
    )


@pytest.fixture
def bad_type_parameters():
    return dict(
        type="Exercise",
        execution_time="2021-01-21T12:24:38+00.00",
        task="TEST_TASK",
        dag_class='test.datalabs.etl.dag.test_resolve.TestDAG'
    )
