""" source: datalabs.task """
import os

import pytest

from   datalabs.task import Task, TaskWrapper

def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


def test_task_is_not_abstract():
    GoodTask(None).run()


def test_task_wrapper_is_not_abstract():
    os.environ['TASK_CLASS'] = 'test.datalabs.test_task.GoodTask'
    GoodTaskWrapper().run()


def test_task_class_name_property_returns_fully_qualified_class_name():
    assert BadTask.name == "test.datalabs.test_task.BadTask"


# pylint: disable=abstract-method
class BadTask(Task):
    pass


class GoodTask(Task):
    def run(self):
        pass


class GoodTaskWrapper(TaskWrapper):
    @classmethod
    def _merge_parameters(cls, parameters, new_parameters):
        return parameters

    def _get_task_parameters(self):
        pass

    def _handle_success(self) -> (int, dict):
        pass

    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass
