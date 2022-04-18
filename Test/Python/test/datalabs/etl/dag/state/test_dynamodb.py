""" Source: datalabs.etl.dag.schedule.dynamodb """
import logging
import os

import pytest

from   datalabs.etl.dag.state import Status
from   datalabs.etl.dag.state.dynamodb import DAGState

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
def test_set_get_dag_status():
    state = DAGState(dict(
        STATE_LOCK_TABLE="DataLake-scheduler-locks-sbx",
        DAG_STATE_TABLE="DataLake-dag-state-sbx"
    ))
    dag = "MY_SWEET_DAG"
    execution_time = "2021-01-01T00:00:00.000000"

    status = state.get_dag_status(dag, execution_time)
    assert status == Status.UNKNOWN

    state.set_dag_status(dag, execution_time, Status.PENDING)
    status = state.get_dag_status(dag, execution_time)
    assert status == Status.PENDING


@pytest.mark.skipif(
    os.getenv('RUN_INTEGRATION_TESTS') != 'True',
    reason="Normally skip integration tests to increase testing speed."
)
def test_set_get_task_status():
    state = DAGState(dict(
        STATE_LOCK_TABLE="DataLake-scheduler-locks-sbx",
        DAG_STATE_TABLE="DataLake-dag-state-sbx"
    ))
    dag = "MY_SWEET_DAG"
    task = "DO_SOMETHING_AWESOME"
    execution_time = "2021-01-01T00:00:00.000000"

    status = state.get_task_status(dag, task, execution_time)
    assert status == Status.UNKNOWN

    state.set_task_status(dag, task, execution_time, Status.PENDING)
    status = state.get_task_status(dag, task, execution_time)
    assert status == Status.PENDING
