'''Iqvia stuffs'''
import os
import pandas as pd
import settings
from datalabs.access.edw import EDW

def get_query():
    '''iqvia query'''
    iqvia_query = \
        """ 
        SELECT DISTINCT 
        B.BUSINESS_NAME as "Oooh",
        B.DBA_NAME,
        B.PHONE,
        B.PHYSICAL_ADDR_1,
        B.PHYSICAL_ADDR_2,
        B.PHYSICAL_CITY,
        B.PHYSICAL_STATE,
        B.PHYSICAL_ZIP,
        B.POSTAL_ADDR_1,
        B.POSTAL_ADDR_2,
        B.POSTAL_CITY,
        B.POSTAL_STATE,
        B.POSTAL_ZIP,
        P.ME,
        T.AFFIL_TYPE_DESC,
        A.AFFIL_IND,
        A.AFFIL_RANK
        FROM 
        ODS.ODS_IMS_BUSINESS B, ODS.SAS_ODS_IMS_PROVIDER_AFFIL A, ODS.ODS_IMS_PROFESSIONAL P, ODS.ODS_IMS_AFFILIATION_TYPE T
        WHERE  
        B.IMS_ORG_ID = A.IMS_ORG_ID
        AND
        A.PROFESSIONAL_ID = P.PROFESSIONAL_ID
        AND
        A.AFFIL_TYPE_ID = T.AFFIL_TYPE_ID
        AND
        P.CURRENT_BATCH_FLAG='Y'
        AND
        A.CURRENT_BATCH_FLAG='Y'
        AND
        B.CURRENT_BATCH_FLAG='Y'
        """
    return iqvia_query

def iqvia():
    query = get_query()
    with EDW() as edw:
        iqvia = edw.read(query)
    return iqvia