""" Transformer tasks for ODS (IQVIA + Symphony) data processing and preparation """
# pylint: disable=import-error,trailing-whitespace
from dataclasses import dataclass
from io import BytesIO, StringIO
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.analysis.address.scoring.etl.transform.cleanup import clean_data, get_me10_to_me11_mapping
from datalabs.analysis.address.scoring.etl.transform.address_key import add_address_key


class ODSDataProcessorTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':

        data = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep='|', dtype=str)
        data = clean_data(data)

        # base data with ME number column (needed for expanding 10 char ME to 11 char ME)
        me_data = pd.read_csv(StringIO(self._parameters['data'][1].decode()), sep='|', dtype=str)
        me_data = clean_data(me_data)

        col_street = self._parameters['street_address_column']
        col_zip = self._parameters['zip_column']

        data = add_address_key(data, col_street, col_zip)
        me10_to_me11_mapping = get_me10_to_me11_mapping(me_data['me'].values)

        data['me'] = data['ims_me'].map(me10_to_me11_mapping)

        data = data[~data['me'].isna()]

        data = data[['me', 'address_key']]
        results = BytesIO()
        data.to_csv(results, sep='|', index=False)
        results.seek(0)
        return [results.getvalue()]
