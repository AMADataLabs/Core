# Kari Palmier    Created 8/22/19
#
#############################################################################
import os
import sys

import pandas as pd
import pyodbc

import datalabs.curate.dataframe  # pylint: disable=unused-import


def get_iqvia_sample_info(ODS_conn):
    
    ims_query = \
        """
            SELECT
            p.ME AS IMS_ME,
            b.PHYSICAL_ADDR_2 AS IMS_POLO_MAILING_LINE_1,
            b.PHYSICAL_ADDR_1 AS IMS_POLO_MAILING_LINE_2,
            b.PHYSICAL_CITY AS IMS_POLO_CITY,
            b.PHYSICAL_STATE AS IMS_POLO_STATE,
            b.PHYSICAL_ZIP AS IMS_POLO_ZIP,
            b.PHONE AS IMS_TELEPHONE_NUMBER,
            b.FAX AS IMS_FAX_NUMBER
            FROM
            ODS.ODS_IMS_BUSINESS b, ODS.SAS_ODS_IMS_PROVIDER_BEST_AFFIL a, ODS.ODS_IMS_PROFESSIONAL p 
            WHERE
            p.PROFESSIONAL_ID = a.PROFESSIONAL_ID
            AND
            a.IMS_ORG_ID = b.IMS_ORG_ID
            AND
            p.CURRENT_BATCH_FLAG = 'Y'
            AND
            a.CURRENT_BATCH_FLAG = 'Y'
            AND
            b.CURRENT_BATCH_FLAG = 'Y'
            AND
            b.PHONE <> '3143626848'        
        """    
        
    iqvia_dpc_df = pd.read_sql(ims_query, ODS_conn)
    
    iqvia_dpc_df = iqvia_dpc_df.datalabs.strip()
    
    return iqvia_dpc_df


def get_iqvia_all_phys_info(ODS_conn):
    
    ims_query = \
        """
            SELECT
            p.ME AS IMS_ME,
            b.PHYSICAL_ADDR_2 AS IMS_POLO_MAILING_LINE_1,
            b.PHYSICAL_ADDR_1 AS IMS_POLO_MAILING_LINE_2,
            b.PHYSICAL_CITY AS IMS_POLO_CITY,
            b.PHYSICAL_STATE AS IMS_POLO_STATE,
            b.PHYSICAL_ZIP AS IMS_POLO_ZIP,
            b.PHONE AS IMS_TELEPHONE_NUMBER,
            b.FAX AS IMS_FAX_NUMBER
            FROM
            ODS.ODS_IMS_BUSINESS b, ODS.SAS_ODS_IMS_PROVIDER_BEST_AFFIL a RIGHT OUTER JOIN ODS.ODS_IMS_PROFESSIONAL p 
            ON
            p.PROFESSIONAL_ID = a.PROFESSIONAL_ID
            WHERE
            a.IMS_ORG_ID = b.IMS_ORG_ID
            AND
            p.CURRENT_BATCH_FLAG = 'Y'
            AND
            a.CURRENT_BATCH_FLAG = 'Y'
            AND
            b.CURRENT_BATCH_FLAG = 'Y'
        """    
        
    iqvia_dpc_df = pd.read_sql(ims_query, ODS_conn)
    
    iqvia_dpc_df = iqvia_dpc_df.datalabs.strip()
    
    return iqvia_dpc_df


def get_symphony_sample_info(ODS_conn):
    
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
            	and
            	l.ID_QLFR_TYP_CDE = 38
            	and
            	d.ADDR_FRST_TLPHN_NBR <> '(314) 362-6848'
    
        """    
        
    sym_dpc_df = pd.read_sql(sym_dpc_query, ODS_conn)
    
    sym_dpc_df['SYM_TELEPHONE_NUMBER'] = sym_dpc_df['SYM_TELEPHONE_ORIG'].apply(lambda x: x.replace('(', 
              '').replace(')', '').replace(' ', '').replace('-', '') if x != None else x)
    sym_dpc_df['SYM_FAX_NUMBER'] = sym_dpc_df['SYM_FAX_ORIG'].apply(lambda x: x.replace('(', 
              '').replace(')', '').replace(' ', '').replace('-', '') if x != None else x)
    
    sym_dpc_df = sym_dpc_df.datalabs.strip()
    
    return sym_dpc_df


def get_symphony_all_phys_info(ODS_conn):
    
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
            	and
            	l.ID_QLFR_TYP_CDE = 38
    
        """    
        
    sym_dpc_df = pd.read_sql(sym_dpc_query, ODS_conn)
    
    sym_dpc_df['SYM_TELEPHONE_NUMBER'] = sym_dpc_df['SYM_TELEPHONE_ORIG'].apply(lambda x: x.replace('(', 
              '').replace(')', '').replace(' ', '').replace('-', '') if x != None else x)
    sym_dpc_df['SYM_FAX_NUMBER'] = sym_dpc_df['SYM_FAX_ORIG'].apply(lambda x: x.replace('(', 
              '').replace(')', '').replace(' ', '').replace('-', '') if x != None else x)
    
    sym_dpc_df = sym_dpc_df.datalabs.strip()
    
    return sym_dpc_df



