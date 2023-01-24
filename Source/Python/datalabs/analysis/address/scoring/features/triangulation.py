""" Generic triangulation data source definition and functions for address triangulation """
from   dataclasses import dataclass
from   collections import namedtuple

import pandas as pd

from   datalabs import feature
from   datalabs.analysis.address.scoring.features.column import ADDRESS_STANDARD_COLUMNS, REQUIRED_COLUMNS
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

pd.set_option('max_columns', None)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class TriangulationFeatureTransformerParameters:
    as_of_date: str
    triangulation_source: str
    execution_time: str = None


class TriangulationFeatureTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = EntityCommFeatureGenerationTransformerParameters
    TriangulationDataSource = namedtuple("TriangulationDataSource", "data source_name")

    def run(self) -> 'list<bytes>':
        base_data, triangulations_data = [self._csv_to_dataframe(d, sep='|', dtype=str) for d in self._data]
        as_of_date = self._parameters.as_of_date
        triangulations = self.TriangulationDataSource(triangulations_data, self._parameters.triangulation_source)

        features = self._add_triangulation_features(base_data, triangulations, as_of_date)

        return [self._dataframe_to_csv(features, sep='|')]

    @classmethod
    def _add_triangulation_features(
        cls,
        base_data: pd.DataFrame,
        triangulations: TriangulationDataSource,
        as_of_date: str
    ):
        # 1. find if base_data ME-address_key pair exists in triangulation
        # 2. find if OTHER address_key values exist for each ME-address_key pair
        base_data.columns = [col.upper() for col in base_data.columns]

        triangulations.rename(columns=REQUIRED_COLUMNS)

        base_data['ME10'] = base_data['ME'].apply(lambda x: x[:10])  # IQVIA and Symphony ME numbers are only first 10 chars
        if 'ADDRESS_KEY' not in base_data.columns.values:
            base_data['ADDRESS_KEY'] = cls.__standardize_address_in_address_key(base_data['ADDR_LINE2'])

        base_data['ME_ADDRESS_KEY'] = base_data['ME10'] + '_' + base_data['ADDRESS_KEY']
        base_data['ME_ADDRESS_KEY'] = base_data['ME_ADDRESS_KEY'].apply(str.upper)

        if 'AS_OF_DATE' in triangulations.data.columns:
            triangulations.data = triangulations.data[triangulations.data['AS_OF_DATE'] <= as_of_date]

        triangulation_pairs = triangulations.data[['ME', 'ADDRESS_KEY']].drop_duplicates()

        triangulation_pairs['ADDRESS_KEY'] = triangulation_pairs['ADDRESS_KEY'].fillna('').astype(str)

        triangulation_pairs['ME_ADDRESS_KEY'] = triangulation_pairs['ME'].fillna('').astype(str) + '_' + \
                                                triangulation_pairs['ADDRESS_KEY']

        triangulation_pairs['ME_ADDRESS_KEY'] = triangulation_pairs['ME_ADDRESS_KEY'].str.upper().apply(
            cls._standardize_address_in_me_address_key
        )

        # only keep triangulation data with actual address keys populated (with zip code)
        triangulation_pairs = triangulation_pairs[triangulation_pairs['ADDRESS_KEY'].apply(lambda x: not x.endswith('_'))]

        agreement_colname = f'TRIANGULATION_{triangulations.source_name}_AGREEMENT'
        other_colname = f'TRIANGULATION_{triangulations.source_name}_OTHER'

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

    @classmethod
    def _standardize_address_in_me_address_key(cls, me_address_key):
        sections = me_address_key.split('_')

        if len(sections) != 3:
            standardized_address_key = me_address_key  # data is messed up.

        me, address, zip = sections
        address = cls._standardize_address_words(address)

        standardized_address_key = f'{me}_{address}_{zip}'

        return standardized_address_key

    @classmethod
    def _standardize_address_in_address_key(cls, address_key):
            return base_data['ADDR_LINE2'].fillna('').str.upper().apply(
                cls._standardize_address_words
            ) + '_' + base_data['ZIP'].fillna('')

    @classmethod
    def _standardize_address_words(cls, text):
        tokens = text.split()
        result = []
        for token in tokens:
            if token in ADDRESS_STANDARD_COLUMNS:
                result.append(ADDRESS_STANDARD_COLUMNS[token])
            else:
                result.append(token)
        return ' '.join(result)
