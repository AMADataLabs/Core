import os

import jaydebeapi

aims = jaydebeapi.connect(
  'com/informix/jdbc/IfxConnection',
  # 'jdbc:informix-sqli://rdbp1627.ama-assn.org:22093/aims_prod:informixserver=prd1srvxnet',
  'jdbc:informix-sqli://rdbt1511.ama-assn.org:22035/test_100_pct:informixserver=t100srvxnet',
  [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
  ['./jdbc-4.50.4.1.jar', './bson-4.2.0.jar']
)

curs = aims.cursor()
curs.execute('select first 50 * from entity_comm_at')
results = curs.fetchall()
print(results)
