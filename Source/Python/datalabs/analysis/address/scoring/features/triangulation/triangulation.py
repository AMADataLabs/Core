""" Generic triangulation data source definition and functions for address triangulation """
# pylint: disable=import-error
import pandas as pd
from datalabs.etl.transform import TransformerTask
pd.set_option('max_columns', None)

# ADDRESS_KEY takes the following format: f"{street_address}_{zip}"
REQUIRED_COLUMNS = ['ME', 'ADDRESS_KEY', 'SOURCE', 'AS_OF_DATE']


class TriangulationDataSource:
    def __init__(self, file_or_buffer, source_name):
        self.file_or_buffer = file_or_buffer
        self.source_name = source_name
        self.data = pd.read_csv(self.file_or_buffer, sep='|', dtype=str)


def add_triangulation_features(base_data: pd.DataFrame, triangulation_data: TriangulationDataSource, as_of_date: str):
    # 1. find if base_data ME-address_key pair exists in triangulation
    # 2. find if OTHER address_key values exist for each ME-address_key pair
    base_pairs = base_data[['ME', 'ADDRESS_KEY']].drop_duplicates()
    base_pairs['ADDRESS_KEY'] = base_pairs['ADDRESS_KEY'].fillna('').astype(str)

    triangulation_data.data = triangulation_data.data[triangulation_data.data['AS_OF_DATE'] <= as_of_date]

    triangulation_pairs = triangulation_data.data[['ME', 'ADDRESS_KEY']].drop_duplicates()
    triangulation_pairs['ADDRESS_KEY'] = triangulation_pairs['ADDRESS_KEY'].fillna('').astype(str)

    base_pairs = [
        f"{me}_{key}" for me, key in zip(base_pairs['ME'].values, base_pairs['ADDRESS_KEY'].values)
    ]
    triangulation_pairs = [
        f"{me}_{key}" if key != '' else None for me, key in zip(
            triangulation_pairs['ME'].values, triangulation_pairs['ADDRESS_KEY'].values
        )
    ]
    triangulation_agreement = {base_pair: base_pair in triangulation_pairs for base_pair in base_pairs}

    # if ME exists in both base and triangulation data but the PAIR does not exist in triangulation, then
    # some other pair must exist for that ME
    triangulation_other = {
        base_pair: base_pair.split('_')[0] in triangulation_data.data['ME'].values and
        base_pair not in triangulation_pairs for base_pair in base_pairs
    }
    feature_data = base_data[['ENTITY_ID', 'ME', 'ADDRESS_KEY']].drop_duplicates()
    feature_data['KEY'] = [
        f"{me}_{key}" for me, key in zip(feature_data['ME'].values, feature_data['ADDRESS_KEY'].values)
    ]
    feature_data[f'TRIANGULATION_{triangulation_data.source_name}_AGREEMENT'] = feature_data['KEY'].apply(
        lambda x: triangulation_agreement[x]
    )
    feature_data[f'TRIANGULATION_{triangulation_data.source_name}_OTHER'] = feature_data['KEY'].apply(
        lambda x: triangulation_other[x]
    )
    return feature_data


class TriangulationFeatureTransformer(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        base_data = self._parameters['data'][0]
        triangulation_data_source = self._parameters['data'][1]
        as_of_date = self._parameters['data'][2]  # "YYYY-MM-DD"
        features = add_triangulation_features(base_data, triangulation_data_source, as_of_date)
        return features
