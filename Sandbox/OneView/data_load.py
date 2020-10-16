'''OneView dataframe load'''
import os
import pandas as pd
import settings
from datalabs.access.edw import EDW
from datalabs.access.ods import ODS
from datalabs.access.datamart import DataMart
import json

def get_ppd_query():
    '''Get ppd query'''
    ppd_query = \
        """
        SELECT DISTINCT
        PE.ME_NUMBER as medical_education_number,
        PE.LAST_NAME,
        PE.FIRST_NAME,
        PE.MIDDLE_NAME,
        PE.SUFFIX_CODE as name_suffix,
        PE.POLO_ADDR1 as address_line_1,
        PE.POLO_ADDR2 as address_line_2,
        PE.POLO_CITY as city,
        PE.POLO_STATE as state,
        PE.POLO_ZIP as zipcode,
        PE.POLO_PLUS4 as zipcode_plus_4,
        PE.UNDELIVERFLAG as address_undeliverable_flag,
        PE.DEGREE_TYPE as degree,
        PE.BIRTH_YEAR,
        PE.BIRTH_CITY,
        PE.BIRTH_STATE,
        PE.BIRTH_COUNTRY,
        PE.GENDER,
        PE.PREFERREDPHONENUMBER as telephone_number,
        PE.FAXNUMBER as fax_number,
        PE.TOPCODE as type_of_practice,
        PE.PECODE as present_employment,
        PE.MPACODE as major_professional_activity,
        PE.PRIMSPECIALTY as primary_specialty,
        PE.SECONDARYSPECIALTY as secondary_speciality,
        PE.GRADSCHOOLCODE as medical_school,
        PE.GMEHOSPITALID as gme_hospital,
        PE.GMEPRIMSPECIALTY as gme_primary_specialty
        FROM
        ODS.ODS_PPD_FILE PE
        """
    return ppd_query
   
def get_iqvia_queries():
    '''Get iqvia queries'''
    business_query = \
        """
        SELECT DISTINCT
        B.IMS_ORG_ID as id,
        B.BUSINESS_NAME as name,
        B.DBA_NAME as doing_business_as,
        B.PHYSICAL_ADDR_1 as physical_address_one,
        B.PHYSICAL_ADDR_2 as physical_address_two,
        B.PHYSICAL_CITY,
        B.PHYSICAL_STATE,
        B.PHYSICAL_ZIP as phyical_zip_code,
        B.POSTAL_ADDR_1 as postal_address_one,
        B.POSTAL_ADDR_2 as postal_address_two,
        B.POSTAL_CITY,
        B.POSTAL_STATE,
        B.POSTAL_ZIP as postal_zip_code,
        B.PHONE,
        B.FAX,
        B.WEBSITE,
        B.OWNER_STATUS,
        B.PROFIT_STATUS
        FROM
        ODS.ODS_IMS_BUSINESS B
        """
    provider_query = \
        """
        P.PROFESSIONAL_ID as id,
        P.ME as medical_education_number,
        P.FIRST_NAME,
        P.MIDDLE_NAME,
        P.LAST_NAME,
        P.GEN_SUFFIX as suffix,
        P.DESGINATION,
        P.GENDER,
        P.ROLE,
        P.PRIMARY_SPEC as primary_specialty,
        p.SECONDARY_SPEC as secondary_specialty,
        P.TERTIARY_SPEC as tertiary_specialty,
        P.PRIMARY_PROF_CODE as primary_profession_code,
        P.PRIMARY_PROF_DESC as primary_profession_description,
        P.STATUS_DESC as status_description
        FROM
        ODS.ODS_IMS_PROFESSIONAL P
        """
    provider_affiliation_query = \
        """
        P.IMS_ORG_ID as business_id,
        P.PROFESSIONAL_ID as provider_id,
        A.AFFIL_TYPE_DESC as description,
        P.AFFIL_IND as primary,
        P.AFFIL_RANK as rank
        FROM
        ODS.ODS_IMS_PROVIDER_AFFILIATION_FACT P, ODS.ODS_IMS_AFFILIATION_TYPE A
        WHERE
        P.AFFIL_TYPE_ID = A.AFFIL_TYPE_ID
        """
    return (business_query, provider_query, provider_affiliation_query)

def get_credentialing_queries():
    '''Get credentailing queries'''
    credentialing_customer_query = \
        """
        SELECT DISTINCT
        C.CUSTOMER_KEY as id,
        C.CUSTOMER_NBR as number,
        C.CUSTOMER_ISELL_LOGIN as isell_login,
        C.CUSTOMER_NAME as name,
        C.CUSTOMER_TYPE_DESC as type_description,
        C.CUSTOMER_TYPE as type,
        C.CUSTOMER_CATEGORY_DESC as category_description
        FROM
        AMADM.dim_customer C
        """
    credentialing_order_query = \
        """
        SELECT DISTINCT
        O.ORDER_NUMBER as id,
        O.CUSTOMER_KEY as customer_id,
        O.ORDER_PRODUCT_ID as product_id,
        H.MED_EDU_NBR as medical_education_number,
        D.FULL_DT as date
        FROM
        AMADM.DIM_DATE D, AMADM.FACT_EPROFILE_ORDERS O, AMADM.DIM_PHYSICIAN_HIST H
        WHERE
        D.DATE_KEY = O.ORDER_DT_KEY
        AND
        H.PHYSICIAN_HIST_KEY = O.ORDER_PHYSICIAN_HIST_KEY
        """
    return (credentialing_customer_query, credentialing_order_query)

def get_ppd():
    '''Get ppd'''
    ppd_query = get_ppd_query()
    with ODS() as ods:
        ppd = ods.read(ppd_query)
    return ppd

def get_iqvia():
    '''Get iqvia'''
    business_query, provider_query, provider_affiliation_query = get_iqvia_queries()
    with ODS() as ods:
        business = ods.read(business_query)
        provider = ods.read(provider_query)
        provider_affiliation = ods.read(provider_affiliation_query)
    return (business, provider, provider_affiliation)

def get_credentialing():
    '''Get credentialling'''
    credentialing_order_query, credentialing_customer_query = get_credentialing_queries()
    with DataMart() as datamart:
        credentialing_order = datamart.read(credentialing_order_query)
        credentialing_customer = datamart.read(credentialing_customer_query)
    credentialing_customer.CUSTOMER_KEY = credentialing_customer.CUSTOMER_KEY.astype(str)
    address_file = os.environ.get('CREDENTIALING_ADDRESSES')
    addresses = pd.read_csv(address_file)
    product_file = os.environ.get('CREDENTIALING_PRODUCTS')
    credentialing_product = pd.read_csv(product_file)
    credentialing_customer = pd.merge(credentialing_customer, addresses, on='number')
    return (credentialing_order, credentialing_customer, credentialing_product)

def get_ethnicity():
    '''Get race & ethnicity tables'''


def get_meri():
    '''Get MERI tables'''
