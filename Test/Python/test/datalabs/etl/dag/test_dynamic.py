""" Source: datalabs.etl.dag.dynamic """
import pytest

from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.dag.dynamic import DAGTask
from   datalabs.etl.dag.state import Status


def test_dag_is_executed(dag):
    dag_task = DAGTask({"task_statuses": {}}, [dag.encode()])

    dag_task.run()

    assert dag_task.status == Status.RUNNING
    assert len(dag_task.triggered_tasks) == 1
    assert dag_task.triggered_tasks[0] == "A"


@pytest.fixture
def dag():
    return """
'''dynamic.datalabs.etl.test.TestDAG'''
from   datalabs.etl.dag.dag import DAG

class TestDAG(DAG):
    A: "test.datalabs.etl.dag.bogus.ATask"
    B: "test.datalabs.etl.dag.bogus.BTask"
    C: "test.datalabs.etl.dag.bogus.CTask"
    D: "test.datalabs.etl.dag.bogus.DTask"

TestDAG.A >> TestDAG.B >> TestDAG.D
TestDAG.A >> TestDAG.C >> TestDAG.D
"""
