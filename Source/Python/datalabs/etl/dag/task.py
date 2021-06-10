""" DAG runner task class. """
from   dataclasses import dataclass

from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema(unknowns=True)
@dataclass
class DAGExecutorParameters:
    dag_class: str

class DAGExecutorTask(Task):
    PARAMETER_CLASS = DAGExecutorParameters


    def run(self):
        pass
