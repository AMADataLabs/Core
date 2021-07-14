''' Local DAG plugin executor implementation. '''
from   datalabs.etl.dag.plugin.base import DAGPluginExecutor


class LocalDAGPluginExecutor(DAGPluginExecutor):
    def __init__(self, parameters: dict):
        self._dag_class = parameters["dag_class"]

    def run_dag(self, execution_time, dag):
        pass

    def run_task(self, execution_time, dag, task):
        pass
