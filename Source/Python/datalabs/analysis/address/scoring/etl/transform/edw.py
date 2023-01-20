""" Transformer to add party key for entity ID to an input DataFrame """
# pylint: disable=import-error
from dataclasses import dataclass

from   datalabs.analysis.address.scoring.etl.transform.cleanup import DataCleanerMixin
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EDWIDAdditionTransformerParameters:
    execution_time: str = None


class EDWIDAdditionTransformerTask(CSVReaderMixin, CSVWriterMixin, DataCleanerMixin, Task):
    PARAMETER_CLASS = EDWIDAdditionTransformerParameters

    def run(self) -> 'list<bytes>':
        dataset = [self._csv_to_dataframe(d, sep='|', dtype=str) for d in self._data]

        dataset = [self._clean_data(d) for d in dataset]

        transformed_data = self._merge(dataset)

        return self._dataframe_to_csv(transformed_data, sep='|')

    @classmethod
    def _merge(cls, dataset) -> 'Transformed Data':
        data, party_key_data, post_cd_id_data = dataset

        result = data.merge(party_key_data, on='entity_id', how='left')

        result = result.merge(post_cd_id_data, on='comm_id', how='left')

        return result
