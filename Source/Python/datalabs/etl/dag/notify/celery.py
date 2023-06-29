""" Class for notifying tasks to run via Celery. """
import logging
from   datalabs.etl.dag.local.task import run_dag_processor, run_task_processor

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class CeleryDAGNotifier:
    @classmethod
    def notify(cls, dag, execution_time, parameters: dict):
        run_dag_processor(dag, execution_time, parameters)


class CeleryTaskNotifier:
    @classmethod
    def notify(cls, dag, task, execution_time, parameters: dict):
        run_task_processor(dag, task, execution_time, parameters)
