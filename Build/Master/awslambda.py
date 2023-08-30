import logging
import os

from   datalabs.plugin import import_plugin
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def handler(event, context):
    os.environ['JAVA_HOME'] = '/var/task/jdk'

    try:
        with open("package.txt") as file:
            LOGGER.info(file.read())
    except Exception as exception:
        LOGGER.exception("Error: Unable to read package.txt")

    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=event)

    return task_wrapper.run()
