import logging
import os

from   datalabs.plugin import import_plugin
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def handler(event, context):
    LOGGER.debug("Lambda Event: %s", event)
    LOGGER.debug("Lambda Context: %s", context)
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=event)

    return task_wrapper.run()
