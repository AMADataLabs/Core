""" Transformer tasks for ODS (IQVIA + Symphony) data processing and preparation """
# pylint: disable=import-error,trailing-whitespace
from dataclasses import dataclass
from io import BytesIO
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.analysis.address.scoring.etl.transform.cleanup import clean_data, get_me10_to_me11_mapping
from datalabs.analysis.address.scoring.etl.transform.address_key import add_address_key
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ODSDataProcessorTransformerTaskParameters:
    data: object

    keep_columns: str = None  # comma-separated string of columns EXCLUDING ADDRESS FIELDS to keep. entity_id, comm_id
    street_address_column: str = None  # street address (123 Main St)
    zip_column: str = None  # ZIP code (12345)


class ODSDataProcessorTransformerTask(TransformerTask):
    PARAMETER_CLASS = ODSDataProcessorTransformerTaskParameters

    def _transform(self) -> 'Transformed Data':

        data = pd.read_csv(self._parameters.data[0], sep='|', dtype=str)
        data = clean_data(data)
        me_data = pd.read_csv(self._parameters.data[1], sep='|', dtype=str)
        me_data = clean_data(me_data)

        col_street = self._parameters.street_address_column
        col_zip = self._parameters.zip_column

        data = add_address_key(data, col_street, col_zip)
        me10_to_me11_mapping = get_me10_to_me11_mapping(me_data['me'].values)

        data['me'] = data['ims_me'].apply(lambda x: me10_to_me11_mapping[x] if x in me10_to_me11_mapping else None)

        data = data[~data['me'].isna()]

        data = data[['me', 'address_key']]
        results = BytesIO()
        data.to_csv(results, sep='|', index=False)
        results.seek(0)
        return [results.read()]
