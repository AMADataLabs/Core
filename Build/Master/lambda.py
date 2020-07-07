import os

from   datalabs.plugin import import_plugin


def handler(event, context):
    TaskWrapper = import_plugin(os.getenv('TASK_WRAPPER_CLASS'))
    task = TaskWrapper()

    return task.run(event)
