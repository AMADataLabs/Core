""" source: datalabs.etl.airflow """
import json
import logging
import os

import mock
import pytest

from   datalabs.etl.airflow.task import AirflowTaskWrapper, TaskDataCache
import datalabs.etl.task as etl
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_task_parameters_are_parsed(args, environment):
        task_wrapper = AirflowTaskWrapper(TestTask, parameters=args)
        parameters = task_wrapper._get_task_parameters()

        assert 'DAG_VARIABLE' in parameters.variables
        assert parameters.variables['DAG_VARIABLE'] == 'tootie'
        assert 'TASK_VARIABLE' in parameters.variables
        assert parameters.variables['TASK_VARIABLE'] == 'fruity'


def test_task_input_data_is_loaded(args, environment):
        task_wrapper = AirflowTaskWrapper(TestTask, parameters=args)
        parameters = task_wrapper._get_task_parameters()

        assert parameters.data is not None
        assert len(parameters.data) == 3
        assert parameters.data == ['light', 'and', 'smoothie']

class TestTask(task.Task):
    def run(self):
        pass


class TestTaskDataCache(TaskDataCache):
    def extract_data(self):
        return json.loads(self._variables['DATA'])

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
    os.environ['TEST_DAG__TEST_TASK__CACHE_DATA'] = '["light", "and", "smoothie"]'
    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
