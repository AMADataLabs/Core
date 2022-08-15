""" Address Scoring Feature File Aggregation Transformer Task """
# Parameters:
#   - base_data         - [entity_id]
#   - entity_comm       - [entity_id, comm_id, address_key]
#   - entity_comm_usg   - [comm_id]
#   - license           - [entity_id, comm_id]
#   - humach            - [entity_id, address_key]
#   - triangulation     - [entity_id, address_key]
# pylint: disable=import-error
from io import BytesIO
import pickle as pk
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.etl.fs.extract import LocalFileExtractorTask

KEEP_COLS__BASE_DATA = ['me', 'entity_id']
KEEP_COLS__ENTITY_COMM = ['entity_id', 'comm_id', 'address_key', 'entity_comm_*']
KEEP_COLS__ENTITY_COMM_USG = ['comm_id', 'entity_comm_usg_*']
KEEP_COLS__LICENSE = [
    'entity_id', 'comm_id', 'has_newer_active_license_elsewhere', 'has_older_active_license_elsewhere',
    'has_active_license_in_this_state', 'years_licensed_in_this_state', 'license_this_state_years_since_expiration'
]
KEEP_COLS__HUMACH = ['entity_id', 'address_key', 'humach_*']
KEEP_COLS__TRIANGULATION = ['entity_id', 'address_key', 'triangulation_*']


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
            if not col in found_columns:
                raise ValueError(f'could not find {col} in {found_columns}') # assert col in found_columns
            found_columns_kept.append(col)
    kept_data = pd.DataFrame()
    for col in found_columns_kept:
        kept_data[col] = data[col]
    return kept_data.drop_duplicates()


class FeatureAggregatorTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        base_data = self._pipe_delim_txt_to_dataframe(self._parameters['data'][0])
        features_entity_comm = self._pipe_delim_txt_to_dataframe(self._parameters['data'][1])
        features_entity_comm_usg = self._pipe_delim_txt_to_dataframe(self._parameters['data'][2])
        features_license = self._pipe_delim_txt_to_dataframe(self._parameters['data'][3])
        ### features_humach = self._pipe_delim_txt_to_dataframe(self._parameters['data'][4])
        ### features_triangulation = self._pipe_delim_txt_to_dataframe(self._parameters['data'][5])

        base_data = reduce_to_keep_columns(base_data, KEEP_COLS__BASE_DATA)
        base_data = base_data.sample(50)

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
        ### features_humach = reduce_to_keep_columns(features_humach, KEEP_COLS__HUMACH)
        ### features_triangulation = reduce_to_keep_columns(features_triangulation, KEEP_COLS__TRIANGULATION)

        data = base_data.merge(features_entity_comm, on='entity_id', how='left')
        print('m1', data.memory_usage().sum() / 1024 ** 2)
        data = data.merge(features_entity_comm_usg, on=['comm_id'], how='left')
        print('m2', data.memory_usage().sum() / 1024 ** 2)
        data = data.merge(features_license, on=['entity_id', 'comm_id'], how='left')
        print('m3', data.memory_usage().sum() / 1024 ** 2)
        ### data = data.merge(features_humach, on=['entity_id', 'address_key'], how='left')
        ### data = data.merge(features_triangulation, on=['entity_id', 'address_key'], how='left')

        result = BytesIO()
        data.to_csv(result, sep='|', index=False)
        return [result.getvalue()]

    @classmethod
    def _pickle(cls, result):
        return pk.dumps(result)
    @classmethod
    def _pipe_delim_txt_to_dataframe(cls, file):
        return pd.read_csv(BytesIO(file), sep='|')


e_params = {
    'base_path': '../data/2020-06-24/features/',
    'files': 'BASE_DATA.txt, features__entity_comm__2020-06-24.txt, '
             'features__entity_comm_usg__2020-06-24.txt, features__license__2020-06-24.txt'
}

ext = LocalFileExtractorTask(parameters=e_params)
ext.run()

params = {
    'data': ext.data
}

tf = FeatureAggregatorTransformerTask(parameters=params)
tf.run()

with open('agg_test_out.txt', 'wb') as f:
    f.write(tf.data[0])
