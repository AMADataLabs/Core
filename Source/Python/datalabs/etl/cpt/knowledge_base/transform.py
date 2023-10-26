"""CPT Knowledge Base Transformer"""
import logging
import pandas

from   datalabs.task import Task
from   datalabs.etl.csv import CSVWriterMixin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class KnowledgeBaseTransformerTask(CSVWriterMixin, Task):
    def run(self):
        LOGGER.debug(self._data)
        parsed_data = pandas.read_excel(self._data[0])
        import pdb; pdb.set_trace()

        parsed_data['json'] = parsed_data.apply(lambda x: x.to_json(), axis=1)

        return self._dataframe_to_csv(parsed_data[['json']])
