""" Source: datalabs.etl.dag.execute.local """
import logging

import pytest

from   datalabs.etl.dag.execute.local import LocalDAGExecutorTask
from   datalabs.etl.dag.state import Status

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pylint: disable=redefined-outer-name, protected-access
def test_dag_scheduler_task_integration(dag_parameters):
    dag_executor = LocalDAGExecutorTask(dag_parameters)

    assert dag_executor.status == Status.PENDING

    LOGGER.info('-- Initial run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, 1, Status.RUNNING)

    dag_executor._parameters.task_statuses["EXTRACT_SCHEDULE"] = Status.FINISHED

    LOGGER.info('-- Second run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, 2, Status.RUNNING)

    dag_executor._parameters.task_statuses["SCHEDULE_DAGS"] = Status.FINISHED

    LOGGER.info('-- Third run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, 3, Status.RUNNING)

    dag_executor._parameters.task_statuses["NOTIFY_DAG_PROCESSOR"] = Status.FINISHED

    LOGGER.info('-- Fourth run of the DAG Scheduler DAG --')
    _run_dag(dag_executor, 3, Status.FINISHED)

def _run_dag(dag_executor, notification_count, expected_dag_status):
    dag_executor.run()
    assert len(dag_executor.triggered_tasks) == notification_count
    assert dag_executor.status == expected_dag_status


# pylint: disable=redefined-outer-name
@pytest.fixture
def dag_parameters():
    yield dict(
        DAG_CLASS="datalabs.etl.dag.schedule.dag.DAGSchedulerDAG",
        TASK_STATUSES=dict()
    )
