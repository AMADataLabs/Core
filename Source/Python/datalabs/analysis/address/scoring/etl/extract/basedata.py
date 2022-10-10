""" Get POLO-Eligible address data for given population of entity_ids """
from io import BytesIO, StringIO
import pickle as pk
import pandas as pd
from datalabs.etl.transform import TransformerTask

POLO_ELIGIBLE_TYPES = ['OF', 'HO', 'GROUP']
POLO_ELIGIBLE_SOURCES = [
    'AMC',
    'GROUP',
    'MBSHP-WEB',
    'PHONE-CALL',
    'PPA',
    'WHITE-MAIL',
    'E-MAIL',
    'MBSHP-MAIL',
    'OLDCC',
    'PHNSURV',
    'USC-OUTBND',
    'CME-REG',
    'LOCK_BOX',
    'MBSHP-PHON',
    'MBSHP-PURL',
    'OUTREACH',
    'REQ-CARDS',
    'RES-TIPON',
    'WEBSURV',
    'BATCH',
    'YELLOW',
    'DEA',
    'NPI',
    'ACS',
    'ACXIOMNCOA',
    'LIST-HOUSE',
    'NCOA',
    'OTHER',
    'POLO',
    'PPMA',
    'PRFSOL',
    'MFLOAD',
    'OBSOLETE',
    'ADDR-VER',
    'FAST-TRACK',
    'PUBS',
    'RETURNED',
    'WEB',
    'ACXIOM',
    'ACXIOMLODE',
    'ACXIOMPLUS',
    'ADMIT-HOS',
    'ADVR',
    'AFFIL-GRP',
    'AMA-ORG',
    'CGMT',
    'CGMT-EXC',
    'COA-PS',
    'ECF-CNVRSN',
    'ECI',
    'FEDERATION',
    'GME',
    'INTERACT',
    'INTERNET',
    'MBSHP',
    'MBSHP-OTHR',
    'MRKT-RSRCH',
    'PER',
    'PPS',
    'ROSTER',
    'SCHL-HOSP',
    'STU-MATRIC',
    'MEDEC',
    'ACXIOM-DSF'
]


class PoloEligibleDataTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        ppd = pd.read_csv(StringIO(self._parameters['data'][0].decode()), sep=',', dtype=str)
        ppd.columns = [col.lower() for col in ppd.columns]

        entity_comm = pd.read_csv(StringIO(self._parameters['data'][1].decode()), sep='|', dtype=str)
        post_addr = pd.read_csv(StringIO(self._parameters['data'][2].decode()), sep='|', dtype=str)
        print(post_addr.columns.values)

        if 'top_cd' in ppd.columns:
            ppd = ppd[ppd['top_cd'] == '020']  # filter to DPC
        entity_comm = entity_comm[
            (entity_comm['src_cat_code'].isin(POLO_ELIGIBLE_SOURCES)) |
            (entity_comm['comm_type'].isin(POLO_ELIGIBLE_TYPES))
        ]  # filter to polo-eligible data

        base_data = ppd[['me', 'entity_id']].drop_duplicates()

        base_data = base_data.merge(entity_comm, on='entity_id', how='inner')
        base_data = base_data[['me', 'entity_id', 'comm_id']].drop_duplicates()

        base_data = base_data.merge(post_addr, on='comm_id', how='inner')

        result = StringIO()
        base_data.to_csv('base_data_test.txt', sep='|', index=False)
        base_data.to_csv(result, sep='|', index=False)
        return [result.getvalue()]
