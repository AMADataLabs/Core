""" Applies a pre-trained model to score processed address feature data """
from dataclasses import dataclass
import pickle as pk

import pandas as pd
from   sklearn.preprocessing import MinMaxScaler

from   datalabs.analysis.address.scoring.etl.feature import REQUIRED_FEATURES
from   datalabs.analysis.address.scoring.etl.column \
    import INFO_COLUMNS, FILLMAX_COLUMNS, FILLNEG1_COLUMNS, FILL1_COLUMNS
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class AddressScoringTransformerParameters:
    execution_time: str = None


class AddressScoringTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = AddressScoringTransformerParameters

    def run(self) -> 'list<bytes>':
        pd.set_option('max_columns', None)
        model = pk.loads(self._data[0])
        aggregate_features = self._csv_to_dataframe(self._data[1], sep='|', dtype=str)

        transformed_data = self._score(model, aggregate_features)

        return [self._dataframe_to_csv(transformed_data, sep='|')]

    # pylint: disable=too-many-statements
    def _score(self, model, aggregate_features) -> pd.DataFrame:
        if 'me10' in aggregate_features.columns.values:  # lingering from triangulation
            del aggregate_features['me10']

        found_info_columns = [column for column in INFO_COLUMNS if column in aggregate_features.columns]
        info_data = aggregate_features[found_info_columns]

        aggregate_features.set_index(found_info_columns, inplace=True)
        aggregate_features = self._scale_columns(aggregate_features)
        aggregate_features = self._resolve_null_values(aggregate_features)

        for column in aggregate_features.columns:
            if 'triangulation' in column:
                aggregate_features[column] = aggregate_features[column].fillna(0).astype(int)

        for column in REQUIRED_FEATURES:
            if column not in aggregate_features.columns:
                aggregate_features[column] = 0
        predictions = model.predict_proba(aggregate_features[REQUIRED_FEATURES])
        predictions = [p[1] for p in predictions]
        info_data['score'] = predictions

        return info_data

    @classmethod
    def _scale_columns(cls, data: pd.DataFrame):
        for column in data.columns.values:
            if 'count' in column or 'frequency' in column or '_age' in column or 'years' in column:
                scaler = MinMaxScaler()
                scaled = scaler.fit_transform(data[[column]].fillna(0)).reshape(1, -1)[0]
                data[column] = scaled

        return data

    @classmethod
    def _resolve_null_values(cls, data: pd.DataFrame):
        for column in FILLNEG1_COLUMNS:
            data[column].fillna(-1, inplace=True)

        for column in FILL1_COLUMNS:
            data[column].fillna(1, inplace=True)

        for column in data.columns.values:
            try:
                data[column] = data[column].astype(float)
            except:  # pylint: disable=bare-except
                pass

        for column in FILLMAX_COLUMNS:
            max_value = data[column].dropna().max()
            data[column].fillna(max_value, inplace=True)

        return data.fillna(0)

    @classmethod
    def _resolve_feature_structure(cls, data: pd.DataFrame):
        # removes any extra features generated (likely source-related columns) and sorts column order
        resolved_data = pd.DataFrame()
        resolved_data.index = data.index

        for column in REQUIRED_FEATURES:
            resolved_data[column] = data[column]

        return resolved_data
