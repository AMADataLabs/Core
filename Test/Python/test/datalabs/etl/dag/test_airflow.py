""" source: datalabs.etl.dag.task """
import json
import logging
import os

import pytest

from   datalabs.etl.dag.airflow import DAGTaskWrapper
from   datalabs.etl.dag.cache import TaskDataCache, CacheDirection
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_parameters_are_parsed(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    parameters = task_wrapper._get_task_parameters()

    assert parameters.get("dag") == 'TEST_DAG'
    assert parameters.get("task") == 'TEST_TASK'
    assert parameters.get("execution_time") == '19000101'
    assert 'TEST_TASK' not in parameters
    assert 'OTHER_TASK' not in parameters
    assert parameters.get("TASK_VARIABLE") == 'fruity'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_cache_parameters_are_parsed(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._get_task_parameters()
    input_cache_parameters = task_wrapper._cache_parameters[CacheDirection.INPUT]
    output_cache_parameters = task_wrapper._cache_parameters[CacheDirection.OUTPUT]

    assert input_cache_parameters.get("execution_time") == '19000101'
    assert input_cache_parameters.get("DATA") == '["light", "and", "smoothie"]'
    assert input_cache_parameters.get("STUFF") == 'Hello, there!'
    assert input_cache_parameters.get("QUOTE_ONE") == 'How will this end? - Sheridan'
    assert input_cache_parameters.get("QUOTE_TWO") is None

    assert output_cache_parameters.get("execution_time") == '19000101'
    assert output_cache_parameters.get("THING") == 'I am Batman'
    assert output_cache_parameters.get("STUFF") == 'Dear John'
    assert output_cache_parameters.get("QUOTE_ONE") == 'How will this end? - Sheridan'
    assert output_cache_parameters.get("QUOTE_TWO") is None


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_input_data_is_loaded(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)

    task_wrapper._get_task_parameters()  # required to extract cache parameters

    data = task_wrapper._get_task_input_data()

    assert data is not None
    assert len(data) == 3
    assert data == ['light', 'and', 'smoothie']


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_runtime_parameters_are_included_in_task_parameters(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    parameters = task_wrapper._get_task_parameters()

    assert "dag" in parameters
    assert "task" in parameters
    assert "execution_time" in parameters


# pylint: disable=redefined-outer-name, protected-access
def test_no_cache_env_vars_yields_no_cache_parameters(args):
    task_wrapper = DAGTaskWrapper(parameters=args)
    parameters = task_wrapper._get_task_parameters()

    assert len(parameters) == 3


# pylint: disable=redefined-outer-name, protected-access
def test_no_cache_input_parameters_skips_cache_pull(args):
    task_wrapper = DAGTaskWrapper(parameters=args)
    parameters = task_wrapper._get_task_parameters()

    assert len(parameters) == 3


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_wrapper_runs_successfully(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)

    task_wrapper.run()


# pylint: disable=redefined-outer-name, protected-access
def test_no_cache_output_parameters_skips_cache_push(args, environment):
    dag_parameters = [key for key in os.environ if key.startswith('TEST_DAG__')]

    for dag_parameter in dag_parameters:
        os.environ.pop(dag_parameter)

    task_wrapper = DAGTaskWrapper(parameters=args)

    task_wrapper.run()

    task_wrapper._handle_success()

class DummyTask(Task):
    def run(self):
        pass


class DummyDAGState:
    pass


class DummyTaskDataCache(TaskDataCache):
    def extract_data(self):
        return json.loads(self._parameters['DATA'])

    def load_data(self, output_data):
        pass

@pytest.fixture
def args():
    return ['task.py', 'TEST_DAG__TEST_TASK__19000101']


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['TASK_CLASS'] = 'test.datalabs.etl.dag.test_airflow.DummyTask'
    os.environ['TEST_DAG__DAG_STATE_PARAMETERS'] = '''
        {
            "DAG_STATE_CLASS": "datalabs.etl.dag.state.file.DAGState",
            "BASE_PATH": "./"
        }
    '''
    os.environ['TEST_DAG__TEST_TASK__CACHE_CLASS'] = 'test.datalabs.etl.dag.test_airflow.DummyTaskDataCache'
    os.environ['TEST_DAG__TEST_TASK__CACHE_QUOTE_ONE'] = 'How will this end? - Sheridan'
    os.environ['TEST_DAG__TEST_TASK__TASK_VARIABLE'] = 'fruity'

    os.environ['TEST_DAG__TEST_TASK__CACHE_INPUT_STUFF'] = 'Hello, there!'
    os.environ['TEST_DAG__TEST_TASK__CACHE_INPUT_DATA'] = '["light", "and", "smoothie"]'
    os.environ['TEST_DAG__TEST_TASK__CACHE_OUTPUT_THING'] = 'I am Batman'
    os.environ['TEST_DAG__TEST_TASK__CACHE_OUTPUT_STUFF'] = 'Dear John'
    os.environ['TEST_DAG__OTHER_TASK__CACHE_QUOTE_TWO'] = 'In fire. - Kosh'
    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
