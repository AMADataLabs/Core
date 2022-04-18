""" Source: datalabs.etl.dag.schedule.file """
import logging
import tempfile

import pytest

from   datalabs.etl.dag.state import Status
from   datalabs.etl.dag.state.file import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def test_set_get_dag_status(base_path):
    state = DAGState(dict(BASE_PATH=base_path))
    dag = "MY_SWEET_DAG"
    execution_time = "2021-01-01T00:00:00.000000"

    status = state.get_dag_status(dag, execution_time)
    assert status == Status.UNKNOWN

    state.set_dag_status(dag, execution_time, Status.PENDING)
    status = state.get_dag_status(dag, execution_time)
    assert status == Status.PENDING


# pylint: disable=redefined-outer-name
def test_set_get_task_status(base_path):
    state = DAGState(dict(BASE_PATH=base_path))
    dag = "MY_SWEET_DAG"
    task = "DO_SOMETHING_AWESOME"
    execution_time = "2021-01-01T00:00:00.000000"

    status = state.get_task_status(dag, task, execution_time)
    assert status == Status.UNKNOWN

    state.set_task_status(dag, task, execution_time, Status.PENDING)
    status = state.get_task_status(dag, task, execution_time)
    assert status == Status.PENDING


@pytest.fixture
def base_path():
    with tempfile.TemporaryDirectory() as directory:
        yield directory
