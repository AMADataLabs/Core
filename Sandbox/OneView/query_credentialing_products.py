import os

import jaydebeapi

aims = jaydebeapi.connect(
  'com.ibm.db2.jcc.DB2Jcc',
  'jdbc:db2://rdbp1190.ama-assn.org:54050/prddm',
  ['dlabs', os.getenv('JDBC_PASSWORD')],
  ['./db2jcc4.jar']
)

query = \
"""SELECT * FROM AMADM.DIM_PRODUCT P WHERE P.PRODUCT_ID in ('5234399','5234570','5236659','5236662','5236675','5231269','5231279','5231280','5231281','5231425')"""

'''SELECT DISTINCT P.PRODUCT_ID, P.PRODUCT_DESC FROM AMADM.DIM_PRODUCT P LIMIT 100'''

curs = aims.cursor()
curs.execute(query)
results = curs.fetchall()
print(results)
