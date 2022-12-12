""" Transformer task for address scores batch load file """
from datetime import datetime
from io import BytesIO, StringIO
import pandas as pd
from datalabs.etl.transform import TransformerTask


class AddressScoreBatchFileTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        # has columns: me|entity_id|comm_id|address_key|state_cd|score
        score_data = pd.read_csv(BytesIO(self._parameters['data'][0]), sep='|', dtype=str)
        # has columns: PARTY_ID|ME
        party_id_2_me_data = pd.read_csv(BytesIO(self._parameters['data'][1]), sep='|', dtype=str)
        # has columns: POST_CD_ID|SRC_POST_KEY
        post_cd_2_comm_id_data = pd.read_csv(BytesIO(self._parameters['data'][2]), sep='|', dtype=str)

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
        tmp = pd.DataFrame()
        for col in batchload_columns:
            tmp[col] = batchload_data[col]
        batchload_data = tmp
        del tmp

        print(batchload_data.shape)

        output = BytesIO()
        batchload_data.to_csv(output, sep='|', index=False)
        output.seek(0)
        return [output.getvalue()]
