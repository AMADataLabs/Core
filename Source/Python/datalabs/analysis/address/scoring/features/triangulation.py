""" Generic triangulation data source definition and functions for address triangulation """
# pylint: disable=import-error
from io import BytesIO, StringIO
import pandas as pd
from tqdm import tqdm
from datalabs.etl.transform import TransformerTask
pd.set_option('max_columns', None)

# ADDRESS_KEY takes the following format: f"{street_address}_{zip}"
REQUIRED_COLUMNS = ['ME', 'ADDRESS_KEY']


ADDRESS_STANDARDIZATIONS = {
    'AVENUE': 'AVE',
    'SUITE': 'STE',
    'ROAD': 'RD',
    'PLACE': 'PL',
    'NORTH': 'N',
    'EAST': 'E',
    'SOUTH': 'S',
    'WEST': 'W',
    'BOULEVARD': 'BLVD',
    'STREET': 'ST',
    'DRIVE': 'DR',
    'HIGHWAY': 'HWY',
    'CULVERT': 'CT',
    'PARKWAY': 'PKWY',

    'CENTER': 'CTR',
    'UNIVERSITY': 'UNI',
    'UNIV': 'UNI',
    'HOSPITAL': 'HOSP',
    'HOSPIT': 'HOSP',
}

class TriangulationDataSource:
    def __init__(self, file_or_buffer, source_name):
        self.file_or_buffer = file_or_buffer
        self.source_name = source_name
        data = pd.read_csv(self.file_or_buffer, sep='|', dtype=str)
        data.columns = [col.upper() for col in data.columns]
        self.data = data
        for col in REQUIRED_COLUMNS:
            if col not in self.data.columns.values:
                raise ValueError(f'Missing required column in triangulation data source: {col}')



class TriangulationFeatureTransformer(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        base_data = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep='|', dtype=str)
        triangulation_source_name = self._parameters['triangulation_source']
        triangulation_source = TriangulationDataSource(
            StringIO(self._parameters['data'][1].decode()),
            triangulation_source_name
        )

        as_of_date = self._parameters['as_of_date']
        features = add_triangulation_features(base_data, triangulation_source, as_of_date)

        result = BytesIO()
        features.to_csv(result, sep='|', index=False)
        result.seek(0)

        return [result.getvalue()]

    def add_triangulation_features(base_data: pd.DataFrame, triangulation_data: TriangulationDataSource, as_of_date: str):
        # 1. find if base_data ME-address_key pair exists in triangulation
        # 2. find if OTHER address_key values exist for each ME-address_key pair
        base_data.columns = [col.upper() for col in base_data.columns]

        base_data['ME10'] = base_data['ME'].apply(lambda x: x[:10])  # IQVIA and Symphony ME numbers are only first 10 chars
        if 'ADDRESS_KEY' not in base_data.columns.values:
            base_data['ADDRESS_KEY'] = base_data['ADDR_LINE2'].fillna('').apply(
                str.upper).apply(standardize_address_words) + '_' + base_data['ZIP'].fillna('')

        base_data['ME_ADDRESS_KEY'] = base_data['ME10'] + '_' + base_data['ADDRESS_KEY']
        base_data['ME_ADDRESS_KEY'] = base_data['ME_ADDRESS_KEY'].apply(str.upper)

        if 'AS_OF_DATE' in triangulation_data.data.columns:
            triangulation_data.data = triangulation_data.data[triangulation_data.data['AS_OF_DATE'] <= as_of_date]

        triangulation_pairs = triangulation_data.data[['ME', 'ADDRESS_KEY']].drop_duplicates()



        triangulation_pairs['ADDRESS_KEY'] = triangulation_pairs['ADDRESS_KEY'].fillna('').astype(str)

        triangulation_pairs['ME_ADDRESS_KEY'] = triangulation_pairs['ME'].fillna('').astype(str) + '_' + \
                                                triangulation_pairs['ADDRESS_KEY']

        triangulation_pairs['ME_ADDRESS_KEY'] = triangulation_pairs['ME_ADDRESS_KEY'].apply(
            str.upper
        ).apply(
            standardize_address_in_me_address_key
        )

        # only keep triangulation data with actual address keys populated (with zip code)
        triangulation_pairs = triangulation_pairs[triangulation_pairs['ADDRESS_KEY'].apply(lambda x: not x.endswith('_'))]

        agreement_colname = f'TRIANGULATION_{triangulation_data.source_name}_AGREEMENT'
        other_colname = f'TRIANGULATION_{triangulation_data.source_name}_OTHER'

        base_data[agreement_colname] = 0
        base_data.loc[
            base_data['ME_ADDRESS_KEY'].isin(triangulation_pairs['ME_ADDRESS_KEY']),
            agreement_colname
        ] = 1
        print(agreement_colname, base_data[agreement_colname].sum())

        base_data[other_colname] = 0
        base_data.loc[
            (base_data['ME10'].isin(triangulation_pairs['ME'])) &
            (~base_data[agreement_colname]),
            other_colname
        ] = 1
        print(other_colname, base_data[other_colname].sum())

        feature_data = base_data[['ENTITY_ID', 'ME', 'ADDRESS_KEY', agreement_colname, other_colname]].drop_duplicates()
        return feature_data

    def standardize_address_in_me_address_key(me_address_key):
        sections = me_address_key.split('_')

        if len(sections) != 3:
            return me_address_key  # data is messed up.
        me, address, zip = sections
        address = standardize_address_words(address)
        return f'{me}_{address}_{zip}'

    def standardize_address_words(text):
        tokens = text.split()
        result = []
        for token in tokens:
            if token in ADDRESS_STANDARDIZATIONS:
                result.append(ADDRESS_STANDARDIZATIONS[token])
            else:
                result.append(token)
        return ' '.join(result)
