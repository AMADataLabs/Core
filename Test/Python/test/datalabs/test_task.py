""" source: datalabs.task """
import pytest

from datalabs.task import Task, TaskWrapper


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

    def _generate_response(self) -> (int, dict):
        pass

    def _handle_exception(self, exception: Exception) -> (int, dict):
        pass


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


def test_task_is_not_abstract():
    GoodTask(None).run()


def test_task_wrapper_is_abstract():
    with pytest.raises(TypeError):
        BadTaskWrapper(None)  # pylint: disable=abstract-class-instantiated


def test_task_wrapper_is_not_abstract():
    GoodTaskWrapper(GoodTask).run()


def test_task_lineage_is_bad():
    with pytest.raises(TypeError):
        GoodTaskWrapper('Task Class')
