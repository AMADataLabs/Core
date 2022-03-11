import os

from   datalabs.plugin import import_plugin
import settings


def handler(event, context):
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=event)

    return task_wrapper.run()
