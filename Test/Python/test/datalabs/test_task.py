""" source: datalabs.task """
from   dataclasses import dataclass
import os

from   marshmallow.exceptions import ValidationError
import pytest

from   datalabs.parameter import add_schema
from   datalabs.task import Task, TaskWrapper

def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


def test_task_is_not_abstract():
    GoodTask(None).run()


def test_task_wrapper_is_abstract():
    with pytest.raises(TypeError):
        BadTaskWrapper()  # pylint: disable=abstract-class-instantiated


def test_task_wrapper_is_not_abstract():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_task.GoodTask'
    GoodTaskWrapper().run()


def test_task_lineage_is_bad():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_task.BadTask'
    task_wrapper = GoodTaskWrapper('Task Class')

    with pytest.raises(TypeError):
        task_wrapper.run()


# pylint: disable=abstract-method
class BadTask(Task):
    pass


class GoodTask(Task):
    def run(self):
        pass


class BadTaskWrapper(TaskWrapper):
    pass


class GoodTaskWrapper(TaskWrapper):
    def _get_task_parameters(self):
        pass

    def _handle_success(self) -> (int, dict):
        pass

    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
