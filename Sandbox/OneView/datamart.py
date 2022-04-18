'''Functions to extract datamart data'''
import os
import pandas as pd
import settings
from datalabs.access.datamart import DataMart

#define order query
def get_order_query(months, years):
    '''SQL query to get order table'''
    query = \
    f"""
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
    D.MONTH_NBR in {months}
    AND
    D.YR in {years}
    """
    return query

def get_customer_query():
    '''SQL query to get customer table'''
    query = \
    """
    SELECT DISTINCT
    C.CUSTOMER_KEY,
    C.CUSTOMER_NBR,
    C.CUSTOMER_ISELL_LOGIN,
    C.CUSTOMER_NAME,
    C.CUSTOMER_TYPE_DESC,
    C.CUSTOMER_TYPE,
    C.CUSTOMER_CATEGORY_DESC
    FROM
    AMADM.dim_customer C
    """
    return query      

def newest_delta(path, text):
    '''Get newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def fix_me(me_list):
    '''Add leading zeroes to ME'''
    nums = []
    for num in me_list:
        num = str(num)
        num = num.replace('.0', '')
        if len(num) == 10:
            num = '0' + num
        elif len(num) == 9:
            num = '00' + num
        elif len(num) == 8:
            num = '000' + num
        nums.append(num)
    return nums

def get_datamart_results(months, years, order_type='all', customer_type='all'):
    '''Get results for specific time period'''
    order_query = get_order_query(months, years)
    customer_query = get_customer_query()
    with DataMart() as datamart:
        orders = datamart.read(order_query)
        customers = datamart.read(customer_query)
    customers.CUSTOMER_KEY = customers.CUSTOMER_KEY.astype(str)
    customers = customers.fillna('None')
    if customer_type == 'all':
        class_cust = customers[customers.CUSTOMER_NAME != 'None']
    else:
        class_cust = customers[(customers.CUSTOMER_CATEGORY_DESC.isin(customer_type))
                               &(customers.CUSTOMER_NAME != 'None')]
    if order_type == 'reapp':
        orders = orders[orders.ORDER_PRODUCT_ID.isin([4915514])]
    elif order_type == 'app':
        orders = orders[orders.ORDER_PRODUCT_ID.isin([4915513])]
    else:
        orders = orders[orders.ORDER_PRODUCT_ID.isin([4915513, 4915514])]
    results = pd.merge(orders, class_cust, on='CUSTOMER_KEY').drop_duplicates()
    return results
