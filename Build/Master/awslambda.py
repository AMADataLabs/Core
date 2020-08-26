import os

from   datalabs.plugin import import_plugin
import settings


def handler(event, context):
    task_class = import_plugin(os.environ['TASK_CLASS'])
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task = task_wrapper_class(task_class, parameters=event)

    return task.run()
