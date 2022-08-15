""" Extract EDW party key data """
# pylint: disable=import-error,trailing-whitespace
from io import BytesIO
import pandas as pd
from datalabs.etl.extract import ExtractorTask
from datalabs.access.ods import ODS
from datalabs.analysis.address.scoring.etl.transform.cleanup import clean_data


def get_iqvia_data(ods_connection):
    query = \
        """
            SELECT
                p.ME AS IMS_ME,
                p.LAST_NAME AS IMS_LAST_NAME,
                b.PHYSICAL_ADDR_2 AS IMS_POLO_MAILING_LINE_1,
                b.PHYSICAL_ADDR_1 AS IMS_POLO_MAILING_LINE_2,
                b.PHYSICAL_CITY AS IMS_POLO_CITY,
                b.PHYSICAL_STATE AS IMS_POLO_STATE,
                b.PHYSICAL_ZIP AS IMS_POLO_ZIP,
                b.PHONE AS IMS_TELEPHONE_NUMBER,
                b.FAX AS IMS_FAX_NUMBER
            FROM
                ODS.ODS_IMS_BUSINESS b, ODS.SAS_ODS_IMS_PROVIDER_BEST_AFFIL a 
                RIGHT OUTER JOIN 
                ODS.ODS_IMS_PROFESSIONAL p 
                ON p.PROFESSIONAL_ID = a.PROFESSIONAL_ID
            WHERE
                a.IMS_ORG_ID = b.IMS_ORG_ID
                AND
                p.CURRENT_BATCH_FLAG = 'Y'
                AND
                a.CURRENT_BATCH_FLAG = 'Y'
                AND
                b.CURRENT_BATCH_FLAG = 'Y'
        """
    data = pd.read_sql(query, ods_connection)
    data = clean_data(data)
    return data


def get_symphony_data(ods_connection):
    sym_dpc_query = \
        """
             SELECT
                d.ADDR_LINE_2_TXT AS SYM_POLO_MAILING_LINE_1,
                d.ADDR_LINE_1_TXT AS SYM_POLO_MAILING_LINE_2,
                d.ADDR_CITY_NAM AS SYM_POLO_CITY,
                d.ADDR_ST_CDE AS SYM_POLO_STATE,
                d.ADDR_ZIP_CDE AS SYM_POLO_ZIP,
                d.ADDR_FRST_TLPHN_NBR AS SYM_TELEPHONE_ORIG,
                d.ADDR_FRST_FAX_NBR AS SYM_FAX_ORIG,
                l.OTHER_ID AS SYM_ME
             FROM
                ODS.PRACTITIONER_DEMOGRAPHIC_LAYOUT d, ODS.PRACTITIONER_ADDL_IDS_LAYOUT l
             WHERE
                d.DS_PRCTR_ID = l.DS_PRCTR_ID
                AND
                l.ID_QLFR_TYP_CDE = 38

        """
    data = pd.read_sql(sym_dpc_query, ods_connection)

    data['SYM_TELEPHONE_NUMBER'] = data['SYM_TELEPHONE_ORIG'].apply(
        lambda x: x.replace('(','').replace(')','').replace(' ', '').replace('-', '') if x is not  None else x
    )
    data['SYM_FAX_NUMBER'] = data['SYM_FAX_ORIG'].apply(
        lambda x: x.replace('(','').replace(')', '').replace(' ', '').replace('-', '') if x is not None else x
    )
    data = data.datalabs.strip()
    return data


class IQVIADataExtractorTask(ExtractorTask):

    def _extract(self) -> "Extracted Data":
        print(self._parameters)
        with ODS() as ods:
            ods.connect()
            data = get_iqvia_data(ods_connection=ods)

        data = clean_data(data)

        result = BytesIO()
        data.to_csv(result, sep='|', index=False)

        result.seek(0)
        return [result.read()]


class SymphonyDataExtractorTask(ExtractorTask):

    def _extract(self) -> "Extracted Data":
        print(self._parameters)
        with ODS() as ods:
            data = get_symphony_data(ods_connection=ods)

        data = clean_data(data)

        result = BytesIO()
        data.to_csv(result, sep='|', index=False)

        result.seek(0)
        return [result.read()]
