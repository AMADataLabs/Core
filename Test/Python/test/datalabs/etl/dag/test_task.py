""" source: datalabs.etl.dag.task """
import json
import logging
import os

import pytest

from   datalabs.etl.dag.task import DAGTaskWrapper
from   datalabs.etl.dag.cache import TaskDataCache, CacheDirection
from   datalabs.etl.task import ETLComponentTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_parameters_are_parsed(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    parameters = task_wrapper._get_task_parameters()

    assert 'TEST_TASK' not in parameters
    assert 'OTHER_TASK' not in parameters
    assert 'DAG_VARIABLE' in parameters
    assert parameters['DAG_VARIABLE'] == 'tootie'
    assert 'TASK_VARIABLE' in parameters
    assert parameters['TASK_VARIABLE'] == 'fruity'
    assert 'EXECUTION_TIME' in parameters
    assert parameters['EXECUTION_TIME'] == '19000101'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_cache_parameters_are_parsed(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    task_wrapper._get_task_parameters()
    input_cache_parameters = task_wrapper._cache_parameters[CacheDirection.INPUT]
    output_cache_parameters = task_wrapper._cache_parameters[CacheDirection.OUTPUT]

    assert 'EXECUTION_TIME' in input_cache_parameters
    assert input_cache_parameters['EXECUTION_TIME'] == '19000101'
    assert 'DATA' in input_cache_parameters
    assert input_cache_parameters['DATA'] == '["light", "and", "smoothie"]'
    assert 'EXECUTION_TIME' in output_cache_parameters
    assert output_cache_parameters['EXECUTION_TIME'] == '19000101'
    assert 'THING' in output_cache_parameters
    assert output_cache_parameters['THING'] == 'I am Batman'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_cache_parameters_are_overridden(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    task_wrapper._get_task_parameters()
    input_cache_parameters = task_wrapper._cache_parameters[CacheDirection.INPUT]
    output_cache_parameters = task_wrapper._cache_parameters[CacheDirection.OUTPUT]

    assert 'STUFF' in input_cache_parameters
    assert input_cache_parameters['STUFF'] == 'Hello, there!'
    assert 'STUFF' in output_cache_parameters
    assert output_cache_parameters['STUFF'] == 'Dear John'


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_input_data_is_loaded(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    parameters = task_wrapper._get_task_parameters()

    assert parameters['data'] is not None
    assert len(parameters['data']) == 3
    assert parameters['data'] == ['light', 'and', 'smoothie']


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_runtime_parameters_are_not_included_in_task_parameters(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    parameters = task_wrapper._get_task_parameters()

    assert "dag" not in parameters
    assert "task" not in parameters
    assert "execution_time" not in parameters


# pylint: disable=redefined-outer-name, protected-access
def test_no_cache_env_vars_yields_no_cache_parameters(args):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    parameters = task_wrapper._get_dag_task_parameters()

    assert not parameters


# pylint: disable=redefined-outer-name, protected-access
def test_no_cache_input_parameters_skips_cache_pull(args):
    task_wrapper = DAGTaskWrapper(parameters=args)
    task_wrapper._runtime_parameters = task_wrapper._get_runtime_parameters(task_wrapper._parameters)
    parameters = task_wrapper._get_task_parameters()

    assert len(parameters) == 1
    assert 'EXECUTION_TIME' in parameters


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


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_cache_parameters_omitted_from_task_parameters(args, environment):
    task_wrapper = DAGTaskWrapper(parameters=args)

    task_wrapper.run()

    for parameter in task_wrapper._task_parameters:
        assert not parameter.startswith('CACHE_')

class DummyTask(ETLComponentTask):
    def run(self):
        pass


class DummyTaskDataCache(TaskDataCache):
    def extract_data(self):
        return json.loads(self._parameters['DATA'])

    def load_data(self, output_data):
        pass

@pytest.fixture
def args():
    return ['task.py', 'test_dag__test_task__19000101']


@pytest.fixture
def environment():
    current_environment = os.environ.copy()

    os.environ['TASK_CLASS'] = 'test.datalabs.etl.dag.test_task.DummyTask'
    os.environ['TEST_DAG__DAG_VARIABLE'] = 'tootie'
    os.environ['TEST_DAG__CACHE_CLASS'] = 'test.datalabs.etl.dag.test_task.DummyTaskDataCache'
    os.environ['TEST_DAG__CACHE_STUFF'] = 'JIDFSAF9E0RU90FOV9A0FUD'
    os.environ['TEST_DAG__TEST_TASK__TASK_VARIABLE'] = 'fruity'
    os.environ['TEST_DAG__TEST_TASK__CACHE_INPUT_DATA'] = '["light", "and", "smoothie"]'
    os.environ['TEST_DAG__TEST_TASK__CACHE_INPUT_STUFF'] = 'Hello, there!'
    os.environ['TEST_DAG__TEST_TASK__CACHE_OUTPUT_THING'] = 'I am Batman'
    os.environ['TEST_DAG__TEST_TASK__CACHE_OUTPUT_STUFF'] = 'Dear John'
    os.environ['TEST_DAG__OTHER_TASK__CACHE_QUOTE_ONE'] = 'How will this end? - Sheridan'
    os.environ['TEST_DAG__OTHER_TASK__CACHE_QUOTE_TWO'] = 'In fire. - Kosh'
    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
