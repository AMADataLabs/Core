""" Transformer tasks for ODS (IQVIA + Symphony) data processing and preparation """
from dataclasses import dataclass

import pandas

from   datalabs.analysis.address.scoring.etl.transform.address_key import add_address_key
from   datalabs.analysis.address.scoring.etl.transform.cleanup import DataCleanerMixin
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ODSDataProcessorTransformerParameters:
    street_address_column: str
    zip_column: str
    execution_time: str = None


class ODSDataProcessorTransformerTask(CSVReaderMixin, CSVWriterMixin, DataCleanerMixin, Task):
    PARAMETER_CLASS = ODSDataProcessorTransformerParameters

    def run(self) -> 'list<bytes>':
        data, me_data = [self._csv_to_dataframe(d, sep='|', dtype=str) for d in self._data]

        transformed_data = self._transform(data, me_data)

        return [self._dataframe_to_csv(transformed_data, sep='|')]

    def _transform(self, data, me_data) -> pandas.DataFrame:
        """ me_data: base data with ME number column (needed for expanding 10 char ME to 11 char ME) """
        data = self._clean_data(data)

        me_data = self._clean_data(me_data)

        col_street = self._parameters.street_address_column
        col_zip = self._parameters.zip_column

        data = add_address_key(data, col_street, col_zip)
        me10_to_me11_mapping = self.get_me10_to_me11_mapping(me_data['me'].values)

        data['me'] = data['ims_me'].map(me10_to_me11_mapping)

        data = data[~data['me'].isna()]

        data = data[['me', 'address_key']]

        return [data]

    @classmethod
    def get_me10_to_me11_mapping(cls, me_list: list):
        """
        me_list = list of full, 11 digit ME numbers
        """
        mapping = {}

        for me11 in me_list:
            me10 = me11[:10]
            mapping[me10] = me11

        return mapping
