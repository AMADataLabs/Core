""" Transformer to add party key for entity ID to an input DataFrame """
# pylint: disable=import-error
from dataclasses import dataclass
from io import BytesIO, StringIO
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.analysis.address.scoring.etl.transform.cleanup import clean_data


class EDWIDAdditionTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        data = pd.read_csv(self._parameters.data, sep='|', dtype=str)
        data = clean_data(data)

        party_key_data = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep='|', dtype=str)
        party_key_data = clean_data(party_key_data)

        post_cd_id_data = pd.read_csv(StringIO(self._parameters['data'][1].decode()), sep='|', dtype=str)
        post_cd_id_data = clean_data(post_cd_id_data)

        result = data.merge(party_key_data, on='entity_id', how='left')
        result = result.merge(post_cd_id_data, on='comm_id', how='left')

        result_data = BytesIO()
        result.to_csv(result_data, sep='|', index=False)
        result_data.seek(0)

        return [result_data.getvalue()]
