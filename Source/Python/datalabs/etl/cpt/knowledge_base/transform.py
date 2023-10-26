"""CPT Knowledge Base Transformer"""
import logging
import uuid

from   datalabs.task import Task
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.cpt.knowledge_base.column import KNOWLEDGE_BASE_COLUMNS

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class KnowledgeBaseTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    def run(self):
        LOGGER.debug(self._data)
        knowledge_base = self._csv_to_dataframe(
            self._data[0],
            sep="|",
            skiprows=26,
            encoding="latin1",
            names=KNOWLEDGE_BASE_COLUMNS
        )

        return [self._convert_to_json(knowledge_base).encode("utf-8")]

    @classmethod
    def _convert_to_json(cls, knowledge_base):
        knowledge_base["document_id"] = knowledge_base["id"]

        knowledge_base.loc[:, "id"] = knowledge_base.id.apply(lambda x: uuid.uuid1())

        return knowledge_base.to_json(orient="records", default_handler=str)
