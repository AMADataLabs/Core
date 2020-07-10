import os

from   datalabs.awslambda import TaskWrapper
from   datalabs.plugin import import_plugin
import settings


def handler(event, context):
    task_class = import_plugin(os.getenv('TASK_CLASS'))
    task_wrapper_class = import_plugin(os.getenv('TASK_WRAPPER_CLASS'))
    task = task_wrapper_class(task_class)

    return task.run(event)
