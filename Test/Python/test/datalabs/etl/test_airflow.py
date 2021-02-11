""" source: datalabs.etl.airflow """
import logging
import os

import mock
import pytest

from   datalabs.etl.airflow import S3CachingTaskWrapper
import datalabs.etl.task as etl
import datalabs.task as task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_task_parameters_composed_properly(args):
    task_wrapper = S3CachingTaskWrapper(task_class, parameters=args)


class TestTask(task.Task):
    def run(self):
        pass


@pytest.fixture
def args():
    return ['task.py', 'TEST_DAG__TEST_TASK__19000101']
