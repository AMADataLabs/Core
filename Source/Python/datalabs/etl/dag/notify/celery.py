''' Class for notifying tasks to run via SNS. '''
import logging
from   datalabs.etl.dag.local.task import run_dag_processor, run_task_processor

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class CeleryDAGNotifier:
    def __init__(self):
        pass

    def notify(self, dag, execution_time, parameters: dict):
        config_file = parameters['config_file']
        del parameters['config_file']
        run_dag_processor(dag, execution_time, config_file, parameters)


class CeleryTaskNotifier:
    def __init__(self):
        pass

    def notify(self, dag, task, execution_time, parameters: dict):
        run_task_processor(dag, task, execution_time, parameters)
