""" source: datalabs.etl.airflow """
import json
import logging
import os

import pytest

from   datalabs.etl.airflow.task import AirflowTaskWrapper, TaskDataCache, CacheDirection
from   datalabs.etl.task import ETLComponentTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_parameters_are_parsed(args, environment):
    task_wrapper = AirflowTaskWrapper(TestTask, parameters=args)
    parameters = task_wrapper._get_task_parameters()

    assert 'DAG_VARIABLE' in parameters
    assert parameters['DAG_VARIABLE'] == 'tootie'
    assert 'TASK_VARIABLE' in parameters
    assert parameters['TASK_VARIABLE'] == 'fruity'
    assert 'EXECUTION_TIME' in parameters
    assert parameters['EXECUTION_TIME'] == '19000101'
    assert 'CACHE_INPUT_EXECUTION_TIME' in parameters
    assert parameters['CACHE_INPUT_EXECUTION_TIME'] == '19000101'
    assert 'CACHE_OUTPUT_EXECUTION_TIME' in parameters
    assert parameters['CACHE_OUTPUT_EXECUTION_TIME'] == '19000101'

# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_cache_parameters_are_parsed(args, environment):
    task_wrapper = AirflowTaskWrapper(TestTask, parameters=args)
    parameters = task_wrapper._get_task_parameters()
    input_cache_parameters = task_wrapper._get_cache_parameters(parameters, CacheDirection.Input)
    output_cache_parameters = task_wrapper._get_cache_parameters(parameters, CacheDirection.Output)

    assert 'EXECUTION_TIME' in input_cache_parameters
    assert input_cache_parameters['EXECUTION_TIME'] == '19000101'
    assert 'DATA' in input_cache_parameters
    assert input_cache_parameters['DATA'] == '["light", "and", "smoothie"]'
    assert 'EXECUTION_TIME' in output_cache_parameters
    assert output_cache_parameters['EXECUTION_TIME'] == '19000101'
    assert 'THING' in output_cache_parameters
    assert output_cache_parameters['THING'] == 'I am Batman'



# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_input_data_is_loaded(args, environment):
    task_wrapper = AirflowTaskWrapper(TestTask, parameters=args)
    parameters = task_wrapper._get_task_parameters()

    assert parameters['data'] is not None
    assert len(parameters['data']) == 3
    assert parameters['data'] == ['light', 'and', 'smoothie']


# pylint: disable=redefined-outer-name, protected-access, unused-argument
def test_task_wrapper_runs_successfully(args, environment):
    task_wrapper = AirflowTaskWrapper(TestTask, parameters=args)

    task_wrapper.run()

class TestTask(ETLComponentTask):
    def run(self):
        pass


class TestTaskDataCache(TaskDataCache):
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

    os.environ['TEST_DAG__DAG_VARIABLE'] = 'tootie'
    os.environ['TEST_DAG__CACHE_CLASS'] = 'test.datalabs.etl.airflow.test_task.TestTaskDataCache'
    os.environ['TEST_DAG__TEST_TASK__TASK_VARIABLE'] = 'fruity'
    os.environ['TEST_DAG__TEST_TASK__CACHE_INPUT_DATA'] = '["light", "and", "smoothie"]'
    os.environ['TEST_DAG__TEST_TASK__CACHE_OUTPUT_THING'] = 'I am Batman'
    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
