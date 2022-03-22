import os

import jaydebeapi

database = jaydebeapi.connect(
  'com.ibm.db2.jcc.DB2Jcc',
  'jdbc:db2://rdbd1157.ama-assn.org:50050/DEVSSO',
  [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
  './db2jcc4.jar'
)

curs = database.cursor()

curs.execute('SELECT * FROM sso.PC_USER LIMIT 2')
results = curs.fetchall()
print(results)

curs.execute('SELECT * FROM sso.ORG_USER LIMIT 2')
results = curs.fetchall()
print(results)

curs.execute('SELECT * FROM sso.ORGANIZATION LIMIT 2')
results = curs.fetchall()
print(results)

