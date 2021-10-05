""" Source: datalabs.etl.dag.schedule.dag """
import logging
import tempfile

import pytest

from   datalabs.etl.dag.execute.local import LocalDAGExecutorTask
from   datalabs.etl.dag.state import Status

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pylint: disable=redefined-outer-name, protected-access
def test_dag_scheduler_task_integration(state_base_path, dag_parameters):
    dag_executor = LocalDAGExecutorTask(dag_parameters)
    execution_time = dag_executor._parameters.execution_time
    state = dag_executor._parameters.dag_state_class(dict(base_path=state_base_path))

    assert state.get_dag_status("DAG_SCHEDULER", execution_time) == Status.UNKNOWN

    LOGGER.info('-- Initial run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, state, 1, Status.RUNNING)

    state.set_task_status("DAG_SCHEDULER", "EXTRACT_SCHEDULE", execution_time, Status.FINISHED)

    LOGGER.info('-- Second run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, state, 2, Status.RUNNING)

    state.set_task_status("DAG_SCHEDULER", "SCHEDULE_DAGS", execution_time, Status.FINISHED)

    LOGGER.info('-- Third run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, state, 3, Status.RUNNING)

    state.set_task_status("DAG_SCHEDULER", "NOTIFY_DAG_PROCESSOR", execution_time, Status.FINISHED)

    LOGGER.info('-- Fourth run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, state, 3, Status.FINISHED)


def _run_dag(dag_executor, state, notification_count, expected_dag_status):
    dag_executor.run()
    assert len(dag_executor.triggered_tasks) == notification_count
    assert state.get_dag_status("DAG_SCHEDULER", dag_executor._parameters.execution_time) == expected_dag_status


@pytest.fixture
def state_base_path():
    with tempfile.TemporaryDirectory() as state_base_path:
        yield state_base_path


# pylint: disable=redefined-outer-name
@pytest.fixture
def dag_parameters(state_base_path):
    yield dict(
        DAG="DAG_SCHEDULER",
        DAG_CLASS="datalabs.etl.dag.schedule.dag.DAGSchedulerDAG",
        DAG_STATE_CLASS='datalabs.etl.dag.state.file.DAGState',
        DAG_EXECUTOR_CLASS='datalabs.etl.dag.execute.local.LocalDAGExecutorTask',
        EXECUTION_TIME="2021-01-21T12:24:38.000000",
        BASE_PATH=state_base_path,
        TASK_TOPIC_ARN="arn:aws:sns:us-east-1:012345678901:DataLake-Task-Processor-fake"
    )


# pylint: disable=redefined-outer-name
@pytest.fixture
def task_parameters(state_base_path):
    return dict(
        DAG="DAG_SCHEDULER",
        TASK="REPLACE_ME",
        DAG_CLASS="datalabs.etl.dag.schedule.dag.DAGSchedulerDAG",
        DAG_STATE_CLASS='datalabs.etl.dag.state.file.DAGState',
        TASK_EXECUTOR_CLASS='datalabs.etl.dag.execute.local.LocalTaskExecutorTask',
        EXECUTION_TIME="2021-01-21T12:24:38.000000",
        BASE_PATH=state_base_path,
        TASK_TOPIC_ARN="arn:aws:sns:us-east-1:012345678901:DataLake-Task-Processor-fake"
    )
