import os

import jaydebeapi

database = jaydebeapi.connect(
  'com.mysql.jdbc.Driver',
  'jdbc:mysql://rdsomething.ama-assn.org:12345/dbname',
  [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
  './mysql-connector-java-8.0.23.jar'
)

curs = database.cursor()
curs.execute('SELECT * FROM SOME_TABLE LIMIT 2')
results = curs.fetchall()

print(results)
