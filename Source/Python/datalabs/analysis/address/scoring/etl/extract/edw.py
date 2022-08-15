""" Extract EDW party key data """
# pylint: disable=import-error
from io import BytesIO
import pandas as pd
from datalabs.etl.extract import ExtractorTask
from datalabs.access.edw import EDW, PartyKeyType


class EntityIDPartyKeyExtractorTask(ExtractorTask):

    def _extract(self) -> "Extracted Data":
        print(self._parameters)
        with EDW() as edw:
            data = edw.get_party_keys_by_type(party_key_type=PartyKeyType.ENTITY)

        data.columns = [col.lower() for col in data.columns]
        data['entity_id'] = data['key_val']
        del data['key_val']

        result = BytesIO()
        data.to_csv(result, sep='|', index=False)

        result.seek(0)
        return [result.read()]


class CommIDPostCdExtractorTask(ExtractorTask):

    def _extract(self) -> "Extracted Data":
        print(self._parameters)
        with EDW() as edw:
            data = edw.get_postal_address_map()

        data.columns = [col.lower() for col in data.columns]

        filtered_data = pd.DataFrame()
        filtered_data['post_cd_id'] = data['post_cd_id']
        filtered_data['comm_id'] = data['src_post_key']

        result = BytesIO()
        filtered_data.to_csv(result, sep='|', index=False)

        result.seek(0)
        return [result.read()]
