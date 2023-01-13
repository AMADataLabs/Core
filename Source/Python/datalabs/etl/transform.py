""" Transformer base class and NO-OP implementation. """
import logging

from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PassThroughTransformerTask(Task):
    def run(self):
        log_data = self._parameters.get('LOG_DATA')

        if log_data and log_data.upper() == 'TRUE':
            LOGGER.info('Passed-through Data: %s', self._data)

        return self._data
