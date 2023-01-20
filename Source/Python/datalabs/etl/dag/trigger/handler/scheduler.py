""" DAG Scheduler trigger handler. """
from   datalabs.etl.dag.trigger.handler import task

class TriggerHandlerTask(task.TriggerHandlerTask):
    def _get_dag_parameters(self, event: dict) -> dict:
        return dict(DAG_SCHEDULER={})
