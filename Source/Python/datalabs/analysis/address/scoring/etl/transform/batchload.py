""" Transformer task for address scores batch load file """
from datetime import datetime

import pandas as pd

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ODSDataProcessorTransformerParameters:
    street_address_column: str
    zip_column: str
    execution_time: str = None


class AddressScoreBatchFileTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ODSDataProcessorTransformerParameters

    def run(self) -> 'list<bytes>':
        """
            Expected data:
                has score_data: me|entity_id|comm_id|address_key|state_cd|score
                has party_id_2_me_data: PARTY_ID|ME
                has post_cd_2_comm_id_data: POST_CD_ID|SRC_POST_KEY
        """
        score_data, party_id_2_me_data, post_cd_2_comm_id_data = [
            self._csv_to_dataframe(d, sep='|', dtype=str) for d in self._data
        ]

        transformed_data = self._transform(data, me_data)

        return [self._dataframe_to_csv(transformed_data, sep='|')]

    def _transform(self) -> pd.DataFrame:
        party_id_2_me_data.columns = ['PARTY_ID', 'me']
        post_cd_2_comm_id_data.columns = ['POST_CD_ID', 'comm_id']

        post_cd_2_comm_id_data['comm_id'] = post_cd_2_comm_id_data['comm_id'].fillna('').astype(str).apply(
            lambda x: x.replace('.0', '')
        )
        post_cd_2_comm_id_data['POST_CD_ID'] = post_cd_2_comm_id_data['POST_CD_ID'].fillna('').astype(str).apply(
            lambda x: x.replace('.0', '')
        )
        party_id_2_me_data['PARTY_ID'] = party_id_2_me_data['PARTY_ID'].fillna('').astype(str).apply(
            lambda x: x.replace('.0', '')
        )
        party_id_2_me_data['me'] = party_id_2_me_data['me'].fillna('').astype(str).apply(
            lambda x: x.replace('.0', '')
        )

        data = score_data.merge(party_id_2_me_data, on='me')
        print(data.shape)

        data = data.merge(post_cd_2_comm_id_data, on='comm_id')
        print(data.shape)

        data['AS_OF_DT'] = str(datetime.now().date())
        data['ADDR_SCORE'] = data['score'].astype(float).apply(lambda x: 10.0 * x).apply(round).astype(int)
        data['ADDR_SCORE'] = data['ADDR_SCORE'].astype(int).apply(lambda x: max(x, 1)).apply(lambda x: min(x, 10))

        batchload_columns = ['PARTY_ID', 'POST_CD_ID', 'AS_OF_DT', 'ADDR_SCORE']
        batchload_data = data[batchload_columns].drop_duplicates()

        batchload_data = batchload_data.sort_values(
            by='ADDR_SCORE', ascending=False
        ).groupby(['PARTY_ID', 'POST_CD_ID']).first().reset_index()

        # reorder columns
        reordered_data = pd.DataFrame()
        for column in batchload_columns:
            reordered_data[column] = batchload_data[col]

        return reordered_data
