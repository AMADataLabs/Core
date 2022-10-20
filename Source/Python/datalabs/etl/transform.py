""" Transformer base class and NO-OP implementation. """
from   abc import ABC, abstractmethod

import logging

from   datalabs.etl.task import ETLComponentTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class PassThroughTransformerTask(TransformerTask):
    def run(self):
        log_data = self._parameters.get('LOG_DATA')

        if log_data and log_data.upper() == 'TRUE':
            LOGGER.info('Passed-through Data: %s', self._data)

        return self._data
