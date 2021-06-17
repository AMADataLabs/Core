""" Database object for HSG DataMart """
from   enum import Enum
import logging

from   datalabs.access.odbc import ODBCDatabase

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class ProductType(Enum):
    INITIAL = 4915513
    REAPPOINTMENT = 4915514

class DataMart(ODBCDatabase):
    def get_customers(self):
        LOGGER.info('Customers???')
        sql = """
            SELECT DISTINCT
            CUSTOMER_KEY,
            CUSTOMER_NBR,
            CUSTOMER_ISELL_LOGIN,
            CUSTOMER_NAME,
            CUSTOMER_TYPE_DESC,
            CUSTOMER_TYPE,
            CUSTOMER_CATEGORY_DESC
            FROM AMADM.dim_customer
            """
        data = self.read(sql)
        data.CUSTOMER_KEY = data.CUSTOMER_KEY.astype(str)
        return data

    def get_orders(self, years=(2019, 2020, 2021), product=None):
        if not product:
            products = (ProductType.INITIAL.value, ProductType.REAPPOINTMENT.value)
        elif product == 'app':
            products = (ProductType.INTIAL.value)
        elif product == 'reapp':
            products = (ProductType.REAPPOINMENT.value)
        data = self.read(f"""
            SELECT DISTINCT
            D.FULL_DT,
            H.MED_EDU_NBR AS ME,
            H.PARTY_ID,
            O.ORDER_NBR,
            O.ORDER_PRODUCT_ID,
            O.ORDER_PHYSICIAN_HIST_KEY,
            O.CUSTOMER_KEY
            FROM
            AMADM.DIM_DATE D, AMADM.FACT_EPROFILE_ORDERS O, AMADM.DIM_PHYSICIAN_HIST H
            WHERE
            D.DATE_KEY = O.ORDER_DT_KEY
            AND
            H.PHYSICIAN_HIST_KEY = O.ORDER_PHYSICIAN_HIST_KEY
            AND
            D.YR in {years}
            AND 
            O.ORDER_PRODUCT_ID IN {products}
            """
        )
        return data


            
    