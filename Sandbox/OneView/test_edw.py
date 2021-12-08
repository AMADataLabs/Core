import os

import jaydebeapi

aims = jaydebeapi.connect(
  'com.ibm.db2.jcc.DB2Jcc',
  'jdbc:db2://rdbp1190.ama-assn.org:54000/prddw',
  [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
  ['./db2jcc4.jar']
)

query = '''
SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='COUNTY_ZR'
'''
'''
SELECT schemaname FROM syscat.schemata
'''
'''
SELECT * FROM SYSIBM.SYSTABLES WHERE CREATOR='AMAEDW'"
'''
'''
SELECT CREATOR FROM SYSIBM.SYSTABLES WHERE CREATOR NOT LIKE 'SYS%' AND CREATOR NOT LIKE 'UNC%' AND CREATOR NOT LIKE 'UAC%' AND CREATOR NOT LIKE 'PI%' AND CREATOR NOT LIKE 'RDW%' AND CREATOR NOT LIKE 'DW%'
'''
'''
SELECT NAME FROM SYSIBM.SYSTABLES WHERE CREATOR='AMAEDW'
'''
'''
SELECT NAME FROM SYSIBM.SYSTABLES WHERE CREATOR='AMAEDW' AND NAME LIKE 'ENTITY%'
'''

curs = aims.cursor()
curs.execute(query)
results = curs.fetchall()
print(results)
