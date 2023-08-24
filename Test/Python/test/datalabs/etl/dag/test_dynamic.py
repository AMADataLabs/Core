""" Source: datalabs.etl.dag.dynamic """
import pytest

from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.dag.dynamic import DAGTask
from   datalabs.etl.dag.state import Status


def test_dag_is_executed(dag):
    dag_class = "dynamic.datalabs.etl.test.TestDAG"
    dag_task = DAGTask({"task_statuses": {}}, [dag_class.encode(), dag.encode()])

    dag_task.run()

    assert dag_task.status == Status.RUNNING
    assert len(dag_task.triggered_tasks) == 1
    assert dag_task.triggered_tasks[0] == "A"


@pytest.fixture
def dag():
    return """
from   datalabs.etl.dag.dag import DAG, PythonTask

class TestDAG(DAG):
    A: PythonTask("test.datalabs.etl.dag.bogus.ATask")
    B: PythonTask("test.datalabs.etl.dag.bogus.BTask")
    C: PythonTask("test.datalabs.etl.dag.bogus.CTask")
    D: PythonTask("test.datalabs.etl.dag.bogus.DTask")

TestDAG.A >> TestDAG.B >> TestDAG.D
TestDAG.A >> TestDAG.C >> TestDAG.D
"""
