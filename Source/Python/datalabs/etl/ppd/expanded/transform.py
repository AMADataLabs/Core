"""Expanded PPD transformer"""
# pylint: disable=import-error
from io import StringIO
import pickle as pk
import pandas as pd
from datalabs.etl.parse.transform import ParseToCSVTransformerTask
from datalabs.etl.transform import TransformerTask


COLUMNS = [
            'ME',
            'PARTY_ID',
            'ENTITY_ID',
            'RECORD_ID',
            'UPDATE_TYPE',
            'ADDRESS_TYPE',
            'MAILING_NAME',
            'LAST_NAME',
            'FIRST_NAME',
            'MIDDLE_NAME',
            'SUFFIX',
            'PPMA_POST_CD_ID',
            'PPMA_COMM_ID',
            'MAILING_LINE_1',
            'MAILING_LINE_2',
            'CITY',
            'STATE',
            'ZIP',
            'SECTOR',
            'CARRIER_ROUTE',
            'ADDRESS_UNDELIVERABLE_FLAG',
            'FIPS_COUNTY',
            'FIPS_STATE',
            'PRINTER_CONTROL_CODE',
            'PC_ZIP',
            'PC_SECTOR',
            'DELIVERY_POINT_CODE',
            'CHECK_DIGIT',
            'PRINTER_CONTROL_CODE_2',
            'REGION',
            'DIVISION',
            'GROUP',
            'TRACT',
            'SUFFIX_CENSUS',
            'BLOCK_GROUP',
            'MSA_POPULATION_SIZE',
            'MICRO_METRO_IND',
            'CBSA',
            'CBSA_DIV_IND',
            'MD_DO_CODE',
            'BIRTH_YEAR',
            'BIRTH_CITY',
            'BIRTH_STATE',
            'BIRTH_COUNTRY',
            'GENDER',
            'PREFERRED_PHONE_PHONE_ID',
            'PREFERRED_PHONE_COMM_ID',
            'TELEPHONE_NUMBER',
            'PRESUMED_DEAD_FLAG',
            'PREFERRED_FAX_PHONE_ID',
            'PREFERRED_FAX_COMM_ID',
            'FAX_NUMBER',
            'TOP_CD',
            'PE_CD',
            'PRIM_SPEC_CD',
            'SEC_SPEC_CD',
            'MPA_CD',
            'PRA_RECIPIENT',
            'PRA_EXP_DT',
            'GME_CONF_FLG',
            'FROM_DT',
            'TO_DT',
            'YEAR_IN_PROGRAM',
            'POST_GRADUATE_YEAR',
            'GME_SPEC_1',
            'GME_SPEC_2',
            'TRAINING_TYPE',
            'GME_INST_STATE',
            'GME_INST_ID',
            'MEDSCHOOL_STATE',
            'MEDSCHOOL_ID',
            'MEDSCHOOL_GRAD_YEAR',
            'NO_CONTACT_IND',
            'NO_WEB_FLAG',
            'PDRP_FLAG',
            'PDRP_START_DT',
            'POLO_POST_CD_ID',
            'POLO_COMM_ID',
            'POLO_MAILING_LINE_1',
            'POLO_MAILING_LINE_2',
            'POLO_CITY',
            'POLO_STATE',
            'POLO_ZIP',
            'POLO_SECTOR',
            'POLO_CARRIER_ROUTE',
            'MOST_RECENT_FORMER_LAST_NAME',
            'MOST_RECENT_FORMER_MIDDLE_NAME',
            'MOST_RECENT_FORMER_FIRST_NAME',
            'NEXT_MOST_RECENT_FORMER_LAST',
            'NEXT_MOST_RECENT_FORMER_MIDDLE',
            'NEXT_MOST_RECENT_FORMER_FIRST'
    ]


class ParseToPPDTransformerTask(ParseToCSVTransformerTask):
    def run(self):
        data = super().run()

        data.append(data[0])

        return data


class ExpandedPPDTransformerTask(TransformerTask):
    def _transform(self) -> 'Transformed Data':
        data = pk.loads(self._parameters['data'][0])  # contains file name and the data
        ppd = pd.read_csv(
            StringIO(data[0][1].decode('utf-8')),
            sep=',',
            dtype=str,
            encoding='LATIN',
            names=COLUMNS,
            index_col=False
        )
        filename = data[0][0]
        return [pk.dumps([ppd, filename])]
