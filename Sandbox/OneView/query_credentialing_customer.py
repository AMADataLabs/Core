import os

import jaydebeapi

aims = jaydebeapi.connect(
  'com.ibm.db2.jcc.DB2Jcc',
  'jdbc:db2://rdbp1190.ama-assn.org:54050/prddm',
  ['dlabs', os.getenv('JDBC_PASSWORD')],
  ['./db2jcc4.jar', './']
)

query = \
'''
SELECT DISTINCT C.CUSTOMER_KEY, C.CUSTOMER_NBR, C.CUSTOMER_ISELL_LOGIN, C.CUSTOMER_NAME, C.CUSTOMER_TYPE_DESC, C.CUSTOMER_TYPE, C.CUSTOMER_CATEGORY, C.CUSTOMER_CATEGORY_DESC, C.CURRENT_IND FROM AMADM.dim_customer C 
WHERE C.CUSTOMER_KEY='128275'
'''
curs = aims.cursor()
curs.execute(query)
results = curs.fetchall()
print(results)
