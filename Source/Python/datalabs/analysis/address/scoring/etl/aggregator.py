""" Address Scoring Feature File Aggregation Transformer Task """
# Parameters:
#   - <data source>     - <join on columns to merge with base_data>
#   - base_data         - [entity_id] if APPLICATION, else [entity_id, comm_id] if TRAINING
#   - entity_comm       - [entity_id, comm_id, address_key]
#   - entity_comm_usg   - [comm_id]
#   - license           - [entity_id, comm_id]
#   - humach            - [entity_id, address_key]
#   - triangulation     - [key]
# pylint: disable=import-error,line-too-long,unused-import
from io import BytesIO
import pickle as pk
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.etl.fs.extract import LocalFileExtractorTask


KEEP_COLS__BASE_DATA = ['me', 'entity_id', 'comm_id', 'address_key', 'state_cd', 'survey_date',
                        'comments', 'office_address_verified_updated', 'status' ]
KEEP_COLS__ENTITY_COMM = ['entity_id', 'comm_id', 'entity_comm_*']
KEEP_COLS__ENTITY_COMM_USG = ['comm_id', 'entity_comm_usg_*']
KEEP_COLS__LICENSE = [
    'entity_id', 'comm_id', 'has_newer_active_license_elsewhere', 'has_older_active_license_elsewhere',
    'has_active_license_in_this_state', 'years_licensed_in_this_state', 'license_this_state_years_since_expiration'
]
KEEP_COLS__HUMACH = ['entity_id', 'address_key', 'humach_*']
KEEP_COLS__TRIANGULATION = ['key', 'triangulation_*']


def reduce_to_keep_columns(data: pd.DataFrame, keep_columns: list):
    found_columns = data.columns.values
    found_columns = [col.lower() for col in found_columns]
    data.columns = found_columns
    found_columns_kept = []
    for col in keep_columns:
        if col.endswith('*'):
            for found_col in found_columns:
                if found_col.startswith(col[:-1]):
                    found_columns_kept.append(found_col)
        else:
            if not col in found_columns and col.lower() not in [
                'state_cd', 'survey_date', 'comments', 'office_address_verified_updated', 'status'
            ]:  # these only exist in training data, not current population data
                raise ValueError(f'could not find {col} in {found_columns}') # assert col in found_columns
            found_columns_kept.append(col)
    kept_data = pd.DataFrame()
    for col in found_columns_kept:
        if col in data.columns:
            kept_data[col] = data[col]
    print(kept_data.columns.values)
    return kept_data.drop_duplicates()


class FeatureAggregatorTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        base_data = self._pipe_delim_txt_to_dataframe(self._parameters['data'][0])
        features_entity_comm = self._pipe_delim_txt_to_dataframe(self._parameters['data'][1])
        features_entity_comm_usg = self._pipe_delim_txt_to_dataframe(self._parameters['data'][2])
        features_license = self._pipe_delim_txt_to_dataframe(self._parameters['data'][3])
        features_humach = self._pipe_delim_txt_to_dataframe(self._parameters['data'][4])
        features_triangulation1 = self._pipe_delim_txt_to_dataframe(self._parameters['data'][5])
        features_triangulation2 = self._pipe_delim_txt_to_dataframe(self._parameters['data'][6])

        base_data = reduce_to_keep_columns(base_data, KEEP_COLS__BASE_DATA)
        # base_data = base_data.sample(50)
        base_data['key'] = base_data['me'].fillna('').astype(str) + '_' + base_data['address_key'].fillna('').astype(str)
        print('base_data', base_data.shape, base_data.memory_usage().sum() / 1024**2)
        features_entity_comm = reduce_to_keep_columns(features_entity_comm, KEEP_COLS__ENTITY_COMM)
        print('features_entity_comm', features_entity_comm.shape, features_entity_comm.memory_usage().sum() / 1024**2)
        features_entity_comm_usg = reduce_to_keep_columns(features_entity_comm_usg, KEEP_COLS__ENTITY_COMM_USG)
        print(
            'features_entity_comm_usg',
            features_entity_comm_usg.shape, features_entity_comm_usg.memory_usage().sum() / 1024**2
        )
        features_license = reduce_to_keep_columns(features_license, KEEP_COLS__LICENSE)
        print('features_license', features_license.shape, features_license.memory_usage().sum() / 1024**2)
        features_humach = reduce_to_keep_columns(features_humach, KEEP_COLS__HUMACH)
        features_triangulation1 = reduce_to_keep_columns(features_triangulation1, KEEP_COLS__TRIANGULATION)
        features_triangulation2 = reduce_to_keep_columns(features_triangulation2, KEEP_COLS__TRIANGULATION)

        data = base_data.merge(features_entity_comm, on=['entity_id', 'comm_id'], how='left')
        print('m1', data.memory_usage().sum() / 1024 ** 2)
        data = data.merge(features_entity_comm_usg, on='comm_id', how='left')
        print('m2', data.memory_usage().sum() / 1024 ** 2)
        data = data.merge(features_license, on=['entity_id', 'comm_id'], how='left')
        print('m3', data.memory_usage().sum() / 1024 ** 2)
        data = data.merge(features_humach, on=['entity_id', 'address_key'], how='left')
        # ############### data = base_data.copy()
        base_data.head().to_csv('base_data_head.csv', index=False)
        features_triangulation1.head().to_csv('tri_iqvia_head.csv', index=False)
        features_triangulation2.head().to_csv('tri_symph_head.csv', index=False)
        print('data cols pre')
        print(data.columns.values)
        data = data.merge(features_triangulation1, on=['key'])#, how='left')
        data = data.merge(features_triangulation2, on=['key'])#, how='left')
        print('data cols post')
        print(data.columns.values)

        result = BytesIO()
        data.to_csv(result, sep='|', index=False)
        return [result.getvalue()]

    @classmethod
    def _pickle(cls, result):
        return pk.dumps(result)
    @classmethod
    def _pipe_delim_txt_to_dataframe(cls, file, dtype=str):
        return pd.read_csv(BytesIO(file), sep='|', dtype=dtype)
