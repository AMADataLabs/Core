""" Source: datalabs.etl.dag.dag """
import pytest

from   datalabs.etl.dag import DAG, Repeat


# pylint: disable=redefined-outer-name
def test_dag_task_attributes_are_created(dag_class):
    assert hasattr(dag_class, 'CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY')
    assert hasattr(dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY, 'task_class')
    assert dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY.task_class == TestTask1

    assert hasattr(dag_class, 'POUR_CHAMPAIGN_INTO_GLASS')
    assert hasattr(dag_class.POUR_CHAMPAIGN_INTO_GLASS, 'task_class')
    assert dag_class.POUR_CHAMPAIGN_INTO_GLASS.task_class == TestTask2


# pylint: disable=redefined-outer-name
def test_dag_vertices_are_created(dag_class):
    dag = dag_class()

    assert dag.vertex_size() == 8
    assert dag.edge_size() == 0


# pylint: disable=redefined-outer-name
def test_dag_edges_are_created(dag_class):
    # pylint: disable=pointless-statement
    dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY >> dag_class.POUR_CHAMPAIGN_INTO_GLASS

    dag = dag_class()

    assert dag.edge_size() == 1


# pylint: disable=redefined-outer-name
def test_repeat(dag_class):
    assert hasattr(dag_class, 'WAX_ON_WITH_KARATE_0')
    assert hasattr(dag_class, 'WAX_ON_WITH_KARATE_1')
    assert hasattr(dag_class, 'WAX_ON_WITH_KARATE_2')

    assert not hasattr(dag_class, 'WAX_ON_WITH_KARATE_3')


# pylint: disable=redefined-outer-name
def test_fan_out(dag_class):
    dag_class.fan_out('POUR_CHAMPAIGN_INTO_GLASS', 'WAX_ON_WITH_KARATE')

    dag = dag_class()

    assert dag.edge_size() == 3


# pylint: disable=redefined-outer-name
def test_fan_in(dag_class):
    dag_class.fan_in('WAX_ON_WITH_KARATE', 'CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY')

    dag = dag_class()

    assert dag.edge_size() == 3


# pylint: disable=redefined-outer-name
def test_parallel(dag_class):
    dag_class.parallel('WAX_ON_WITH_KARATE', 'WAX_OFF_WITH_KARATE')

    dag = dag_class()

    assert dag.edge_size() == 3


# pylint: disable=redefined-outer-name
def test_sequence(dag_class):
    dag_class.sequence('WAX_ON_WITH_KARATE')

    dag = dag_class()

    assert dag.edge_size() == 2


# pylint: disable=redefined-outer-name
def test_first(dag_class):
    assert dag_class.WAX_ON_WITH_KARATE_0 == dag_class.first('WAX_ON_WITH_KARATE')


# pylint: disable=redefined-outer-name
def test_last(dag_class):
    assert dag_class.WAX_OFF_WITH_KARATE_2 == dag_class.last('WAX_OFF_WITH_KARATE')


# pylint: disable=redefined-outer-name
def test_predecessors(dag_class):
    dag_class.fan_in('WAX_ON_WITH_KARATE', 'CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY')

    predecessors = dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY.predecessors

    assert len(predecessors) == 3

    for index in range(3):
        task = getattr(dag_class, f'WAX_ON_WITH_KARATE_{index}')

        assert task in predecessors


# pylint: disable=redefined-outer-name
def test_upstream_tasks(dag_class):
    # pylint: disable=expression-not-assigned
    dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY >> dag_class.first('WAX_ON_WITH_KARATE')
    dag_class.sequence('WAX_ON_WITH_KARATE')

    predecessors = dag_class.upstream_tasks('WAX_ON_WITH_KARATE_2')

    assert len(predecessors) == 3
    assert 'CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY' in predecessors
    assert 'WAX_ON_WITH_KARATE_0' in predecessors
    assert 'WAX_ON_WITH_KARATE_1' in predecessors


# pylint: disable=redefined-outer-name
def test_successors(dag_class):
    dag_class.fan_out('CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY', 'WAX_ON_WITH_KARATE')

    successors = dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY.successors

    assert len(successors) == 3

    for index in range(3):
        task = getattr(dag_class, f'WAX_ON_WITH_KARATE_{index}')

        assert task in successors


# pylint: disable=redefined-outer-name
def test_downstream_tasks(dag_class):
    # pylint: disable=expression-not-assigned
    dag_class.CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY >> dag_class.first('WAX_ON_WITH_KARATE')
    dag_class.sequence('WAX_ON_WITH_KARATE')

    successors = dag_class.downstream_tasks('CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY')

    assert len(successors) == 3

    for index in range(3):
        task = f'WAX_ON_WITH_KARATE_{index}'

        assert task in successors


class TestTask1:
    pass


class TestTask2:
    pass


@pytest.fixture
def dag_class():
    class TestDAG(DAG):
        CURE_BOVINE_SPONGIFORM_ENCEPHALOPATHY: TestTask1
        POUR_CHAMPAIGN_INTO_GLASS: TestTask2
        WAX_ON_WITH_KARATE: Repeat(TestTask2, 3)
        WAX_OFF_WITH_KARATE: Repeat(TestTask2, 3)

    return TestDAG
