""" Adds a new column, 'address_key', to input data by combining street address and zip code column values """

# pylint: disable=import-error
from   dataclasses import dataclass

import pandas as pd

from   datalabs.analysis.address.scoring.etl.transform.cleanup import clean_data, get_list_parameter
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AddressKeyTransformerParameters:
    street_address_column: str
    zip_column: str
    keep_columns: str = None
    execution_time: str = None


class AddressKeyTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = AddressKeyTransformerParameters

    def run(self) -> 'list<bytes>':
        data = _csv_to_dataframe(self._data[0], sep='|', dtype=str)

        cleaned_data = self._clean_data(data)

        transformed_data = self._transform(cleaned_data)

        return _dataframe_to_csv(transformed_data, sep='|')

    def _clean_data(self, data):
        return clean_data(data)

    def _transform(self, data):
        col_street = self._parameters.street_address_column]
        col_zip = self._parameters.zip_column]
        result_data = pd.DataFrame()

        data.columns = [col.lower().strip() for col in data.columns.values]
        found_columns = data.columns.values

        if not self._parameters.keep_columns or self._parameters.keep_columns.upper() in ['NONE', '']:
            keep_columns = found_columns
        else:
            keep_columns = get_list_parameter(self._parameters.keep_columns)

        for col in keep_columns:
            result_data[col] = data[col]

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

        return result_data

class SymphonyTransformerTask(AddressKeyTransformerTask):
    def _clean_data(self, data):
        data = clean_data(data)

        data['SYM_TELEPHONE_NUMBER'] = data['SYM_TELEPHONE_ORIG'].apply(
            lambda x: x.replace('(','').replace(')','').replace(' ', '').replace('-', '') if x is not  None else x
        )
        data['SYM_FAX_NUMBER'] = data['SYM_FAX_ORIG'].apply(
            lambda x: x.replace('(','').replace(')', '').replace(' ', '').replace('-', '') if x is not None else x
        )
        data = data.str.strip()

        return data


def add_address_key(data: pd.DataFrame, street_column, zip_column):
    data['address_key'] = data[
        street_column
    ].fillna('').astype(str).apply(str.strip) + '_' + data[
        zip_column
    ].fillna('').astype(str).apply(str.strip)
    data['address_key'] = data['address_key'].apply(str.upper)

    return data
