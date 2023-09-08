""" Daily DAG report tools. """
import logging

from   datalabs.etl.dag.state.dynamodb import DAGState
from   datalabs.etl.dag.util.cron import get_last_days_runs

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def generate_dag_run_report(environment, schedule_path):
    planned_runs = get_last_days_runs(schedule_path)

    run_statuses = get_run_statuses(environment, planned_runs)

    print(run_statuses[~run_statuses.run.isnull()])


def get_run_statuses(environment, dag_runs):
    parameters = dict(
        LOCK_TABLE='N/A',
        STATE_TABLE=f'DataLake-dag-state-{environment}',
    )
    state = DAGState(parameters)

    dag_runs["status"] = dag_runs.apply(
        lambda x: state.get_dag_status(x.dag, x.run.isoformat()).value,
        axis=1
    )

    return dag_runs
