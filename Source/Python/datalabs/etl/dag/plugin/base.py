''' DAG plugin interface classes. '''
from   abc import ABC, abstractmethod


class DAGPluginExecutor(ABC):
    @abstractmethod
    def run_dag(self, execution_time, dag):
        pass

    @abstractmethod
    def run_task(self, execution_time, dag, task):
        pass
