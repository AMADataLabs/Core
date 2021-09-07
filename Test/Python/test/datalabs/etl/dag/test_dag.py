""" Source: datalabs.etl.dag.dag """
from   datalabs.etl.dag import DAG


def test_dag_task_attributes_are_created():
    assert hasattr(TestDAG, 'CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY')
    assert hasattr(TestDAG.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY, 'task_class')
    assert TestDAG.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY.task_class == TestTask1

    assert hasattr(TestDAG, 'POOR_CHAMPAIGN_INTO_GLASS')
    assert hasattr(TestDAG.POOR_CHAMPAIGN_INTO_GLASS, 'task_class')
    assert TestDAG.POOR_CHAMPAIGN_INTO_GLASS.task_class == TestTask2


def test_dag_vertices_are_created():
    dag = TestDAG()

    assert dag.vertex_size() == 2
    assert dag.edge_size() == 0


def test_dag_edges_are_created():
    # pylint: disable=pointless-statement
    TestDAG.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY >> TestDAG.POOR_CHAMPAIGN_INTO_GLASS

    dag = TestDAG()

    assert dag.edge_size() == 1


class TestTask1:
    pass


class TestTask2:
    pass


class TestDAG(DAG):
    CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY: TestTask1
    POOR_CHAMPAIGN_INTO_GLASS: TestTask2
