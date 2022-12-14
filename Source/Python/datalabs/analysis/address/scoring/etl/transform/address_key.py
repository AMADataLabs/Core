""" Adds a new column, 'address_key', to input data by combining street address and zip code column values """

# pylint: disable=import-error
from dataclasses import dataclass
from io import BytesIO, StringIO
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.analysis.address.scoring.etl.transform.cleanup import get_list_parameter


class AddressKeyTransformerTask(TransformerTask):
    # PARAMETER_CLASS = AddressKeyTransformerParameters

    def _transform(self) -> 'Transformed Data':
        data = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep='|', dtype=str)
        if data.columns == 1:  # wrong delim, try comma
            data = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep=',', dtype=str)
        data.columns = [col.lower().strip() for col in data.columns.values]
        found_columns = data.columns.values

        result_data = pd.DataFrame()

        if 'keep_columns' not in self._parameters or str(self._parameters['keep_columns']).upper() in ['NONE', '']:
            keep_columns = found_columns
        else:
            keep_columns = get_list_parameter(self._parameters['keep_columns'])

        for col in keep_columns:
            result_data[col] = data[col]

        col_street = self._parameters['street_address_column']
        col_zip = self._parameters['zip_column']

        if col_street not in found_columns:
            raise KeyError(
                f"Specified street address column '{col_street}' but it "
                f"was not found in input data columns: {found_columns}"
            )
        if col_zip not in found_columns:
            raise KeyError(
                f"Specified ZIP code column '{col_zip}' but it was not found in input data columns: {found_columns}"
            )

        result_data['address_key'] = data[
            col_street
        ].fillna('').astype(str).apply(str.strip) + '_' + data[
            col_zip
        ].fillna('').astype(str).apply(str.strip).apply(lambda x: x[:5])
        result_data['address_key'] = result_data['address_key'].apply(str.upper)

        # keep only ['me', 'address_key'] if data is from IQVIA or Symphony
        if col_street.startswith('ims_'):
            result_data['me'] = result_data['ims_me']
            result_data = result_data[['me', 'address_key']].drop_duplicates()
        elif  col_street.startswith('sym_'):
            result_data['me'] = result_data['sym_me']
            result_data = result_data[['me', 'address_key']].drop_duplicates()

        results = BytesIO()
        result_data.to_csv(results, sep='|', index=False)
        results.seek(0)
        return [results.getvalue()]


def add_address_key(data: pd.DataFrame, street_column, zip_column):
    data['address_key'] = data[
        street_column
    ].fillna('').astype(str).apply(str.strip) + '_' + data[
        zip_column
    ].fillna('').astype(str).apply(str.strip)
    data['address_key'] = data['address_key'].apply(str.upper)
    return data
