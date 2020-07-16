""" source: datalabs.task """
import pytest

from datalabs.task import Task


# pylint: disable=abstract-method
class BadTask(Task):
    pass


class GoodTask(Task):
    def run(self):
        pass


def test_task_is_abstract():
    with pytest.raises(TypeError):
        BadTask(None)  # pylint: disable=abstract-class-instantiated


def test_task_is_not_abstract():
    GoodTask(None).run()
