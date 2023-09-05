''' Base class for the data quality Transformation implementation '''
# pylint: disable=import-error
import csv
import logging

from datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    def run(self):
        LOGGER.debug(self._data)
        metadata = self._parse_metadata(self._parameters.metadata)
        data = self._parse_input(self._data, metadata)
        preprocessed_data = self._preprocess(data)
        entity = self._create_entity(preprocessed_data)
        postprocessed_data = self._postprocess(entity)

        return self._pack(postprocessed_data)

    def _parse_input(self, dataset, metadata):
        return [self._csv_to_dataframe(dataset[i['index']], sep=i['seperator']) for i in metadata.values()]

    def _pack(self, dataset):
        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in dataset]

    # pylint: disable=no-self-use
    def _preprocess(self, dataset):
        return dataset

    # pylint: disable=no-self-use
    def _postprocess(self, dataset):
        return dataset

    # pylint: disable=no-self-use
    def _create_entity(self, dataset):
        return dataset
