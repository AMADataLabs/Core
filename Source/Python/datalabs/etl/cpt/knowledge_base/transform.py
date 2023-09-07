"""SNOMED CPT Transformer"""
import logging
import pandas

from datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DataTransformerTask(Task):
    def run(self):
        LOGGER.debug(self._data)

        parsed_data = pandas.read_excel(self._data[0])

        parsed_data['json'] = parsed_data.apply(lambda x: x.to_json(), axis=1)

        return parsed_data['json']
