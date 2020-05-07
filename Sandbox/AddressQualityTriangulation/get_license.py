'''Check state license'''
import settings
from datalabs.access.edw import EDW

def get_license_query():
    '''Get active license info'''
    sql_query = \
    """
    SELECT DISTINCT
    L.PARTY_ID,
    S.SRC_STATE_CD AS STATE_CD,
    L.LIC_NBR,
    L.FROM_DT,
    L.ISS_DT,
    L.AS_OF_DT
    FROM
    AMAEDW.LIC L, AMAEDW.STATE S
    WHERE
    L.THRU_DT IS NULL
    AND
    L.STATE_ID = S.STATE_ID;
    """
    return sql_query

def get_state_licenses():
    '''Get licenses'''
    license_query = get_license_query()
    with EDW() as edw:
        state_license = edw.read(license_query)
    return state_license
