""" Raw data cleaning transformer tasks for AIMS, EDW, and ODS """
# pylint: disable=import-error
from dataclasses import dataclass
from io import BytesIO
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DataFrameCleanupTransformerTaskParameters:
    data: object
    keep_columns: str = None
    clean_whitespace = True
    date_columns: str = None
    repair_datetime: str = True
    convert_to_int_columns: str = None
    rename_columns: str = None


class DatabaseTableCleanupTransformerTask(TransformerTask):
    PARAMETER_CLASS = DataFrameCleanupTransformerTaskParameters

    def _transform(self) -> 'Transformed Data':
        data = pd.read_csv(BytesIO(self._parameters.data[0]), sep='|')

        results = pd.DataFrame()
        if self._parameters.keep_columns not in [None, '', 'NONE']:
            keep_columns = self._parameters.keep_columns.split(',')
            for col in keep_columns:
                results[col] = data[col].copy()
        else:
            results = data.copy()

        if str(self._parameters.clean_whitespace).upper() == 'TRUE':
            results = clean_whitespace(results)

        if self._parameters.date_columns not in [None, '', 'NONE']:
            cols = get_list_parameter(self._parameters.date_columns)
            for col in cols:
                if str(self._parameters.repair_datetime).upper() == 'TRUE':
                    results[col] = results[col].apply(repair_datetime)
                else:
                    results[col] = pd.to_datetime(results[col])

        if self._parameters.convert_to_int_columns not in [None, '', 'NONE']:
            cols = get_list_parameter(self._parameters.convert_to_int_columns)
            for col in cols:
                results[col] = results[col].apply(convert_to_int)

        if self._parameters.rename_columns not in [None, '', 'NONE']:
            cols = get_list_parameter(self._parameters.rename_columns)
            results.columns = cols

        final_results = BytesIO()
        results.to_csv(final_results, sep='|', index=False)
        final_results.seek(0)

        return [final_results.read()]


def clean_whitespace(data: pd.DataFrame, reduce=True):
    for col in data.columns.values:
        if reduce:
            data[col] = data[col].apply(lambda x: ' '.join(x.strip().split()) if isinstance(x, str) else x)
        else:
            data[col] = data[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return data


def repair_datetime(text):
    if not isinstance(text, str):
        return text
    text = text.strip()
    if len(text) > 10 and text[4] == '/' and text[10] == ':':
        result = text[:10].strip() + ' ' + text[11:].strip()
        return result
    tokens = text.split()
    if len(tokens) > 1 and tokens[1].startswith(':'):
        tokens[1] = tokens[1][1:].strip()
        return ' '.join(tokens)
    return text


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data.columns = [col.lower() for col in data.columns]
    for col in data.columns:
        data[col] = data[col].fillna('').astype(str).apply(str.strip).apply(
            lambda x: x[:-2] if x.endswith('.0') else x
        )
    return data


def convert_to_int(text):
    if isinstance(text, str) and text.isdigit():
        result = str(text)
    elif isinstance(text, float) and str(text).endswith('.0'):
        result = str(text)[:-2]
    else:
        result = text
    return result


def get_list_parameter(parameter):
    if isinstance(parameter, str):
        result = parameter.split(',')
    elif isinstance(parameter, list):
        result = parameter
    else:
        raise ValueError(f'Parameter {parameter} could not be converted / interpreted to list')
    return result


def get_me10_to_me11_mapping(me_list: list):
    """
    me_list = list of full, 11 digit ME numbers
    """
    mapping = {}
    for me11 in me_list:
        me10 = me11[:10]
        mapping[me10] = me11
    return mapping
