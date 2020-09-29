'''Get ppd from ODS'''
import os
import settings
from datalabs.access.ods import ODS

def get_query():
    '''Define ppd query'''
    query = \
    """
    SELECT *
    FROM
    ODS.ODS_PPD_FILE PE
    """
    return query

def get_ppd():
    '''Get ppd'''
    query = get_query()
    with ODS() as ods:
        ppd = ods.read(query)
    return ppd
