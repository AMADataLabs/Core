""" DAG Scheduler trigger handler. """
from   datalabs.etl.dag.trigger.handler import task

class TriggerHandlerTask(task.TriggerHandlerTask):
    def _get_dag_parameters(self, trigger_parameters: dict, event: dict) -> list:
        return [("DAG_SCHEDULER", {})]
