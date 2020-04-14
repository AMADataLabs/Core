'''Grabs processed MEs from database'''
from datalabs.access.edw import EDW
import settings

def get_processed_list():
    '''Get latest processed ME list from EDW'''
    sql_query = \
        """
        SELECT DISTINCT
        M.MED_EDU_NBR
        FROM
        AMAEDW.PERSON M
        WHERE
        M.MORTALITY_STS_CD ='C'
        OR
        M.MORTALITY_STS_CD ='P';
        """

    with EDW() as edw:
        known_mortality_status = edw.read(sql_query)

    processed_mes = list(known_mortality_status.MED_EDU_NBR)

    return processed_mes

def remove_processed_mes(physicians):
    '''Remove physicians whose ME numbers are already processed'''
    processed_list = get_processed_list()
    unprocessed_physicians = physicians[physicians.ME.isin(processed_list)==False]

    return unprocessed_physicians
