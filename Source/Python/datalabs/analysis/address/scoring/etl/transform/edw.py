""" Transformer to add party key for entity ID to an input DataFrame """
# pylint: disable=import-error
from dataclasses import dataclass
from io import BytesIO
import pandas as pd
from datalabs.etl.transform import TransformerTask
from datalabs.parameter import add_schema
from datalabs.analysis.address.scoring.etl.transform.cleanup import clean_data


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EDWIDAdditionTransformerTaskParameters:
    data: object
    party_key_data: object
    post_cd_id_data: object


class EDWIDAdditionTransformerTask(TransformerTask):
    PARAMETER_CLASS = EDWIDAdditionTransformerTaskParameters

    def _transform(self) -> 'Transformed Data':
        data = pd.read_csv(self._parameters.data, sep='|', dtype=str)
        data = clean_data(data)

        party_key_data = pd.read_csv(self._parameters.party_key_data, sep='|', dtype=str)
        party_key_data = clean_data(party_key_data)

        post_cd_id_data = pd.read_csv(self._parameters.post_cd_id_data, sep='|', dtype=str)
        post_cd_id_data = clean_data(post_cd_id_data)

        result = data.merge(party_key_data, on='entity_id', how='left')
        result = result.merge(post_cd_id_data, on='comm_id', how='left')

        result_data = BytesIO()
        result.to_csv(result_data, sep='|', index=False)
        result_data.seek(0)

        return [result_data.read()]
