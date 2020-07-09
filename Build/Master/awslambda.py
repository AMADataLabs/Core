import os

from   datalabs.awslambda import TaskWrapper
from   datalabs.plugin import import_plugin
import settings


def handler(event, context):
    task_class = import_plugin(os.getenv('TASK_CLASS'))
    task = TaskWrapper.create(task_class)

    return task.run(event)
