import os

import jaydebeapi

database = jaydebeapi.connect(
    'com.ibm.db2.jcc.DB2Driver',
    # 'jdbc:db2://rdbd1156.ama-assn.org:50050/edevods',
    'jdbc:db2://rdbt1171.ama-assn.org:52100/etstods',
    # 'jdbc:db2://rdbp1190.ama-assn.org:54150/eprdods',
    # 'jdbc:db2://rdbd1156.ama-assn.org:50000/devdw',
    # 'jdbc:db2://rdbp1190.ama-assn.org:54000/prddw',
    [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
    './DB2JdbcDriver/db2jcc4.jar'
)

curs = database.cursor()
# EDW
# curs.execute('select PARTY_ID, KEY_VAL from AMAEDW.PARTY_KEY LIMIT 10')
# curs.execute('SELECT PARTY_ID, KEY_TYPE_ID, KEY_VAL FROM AMAEDW.PARTY_KEY WHERE KEY_TYPE_ID=18 ORDER BY KEY_VAL LIMIT 10')
# curs.execute('SELECT COUNT(PARTY_ID) FROM AMAEDW.PARTY_KEY')  # All PARTY_KEY count
# curs.execute('SELECT COUNT(PARTY_ID) FROM AMAEDW.PARTY_KEY WHERE KEY_TYPE_ID=18')  # ME count
# curs.execute('SELECT COUNT(PARTY_ID) FROM AMAEDW.PARTY_KEY WHERE KEY_TYPE_ID=38')  # NPI count
# curs.execute('SELECT COUNT(PARTY_ID) FROM AMAEDW.PARTY_KEY WHERE KEY_TYPE_ID=9')  # Entity ID count
# curs.execute('SELECT COUNT(PARTY_ID) FROM AMAEDW.PARTY_KEY WHERE KEY_TYPE_ID=9 OR KEY_TYPE_ID=18 OR KEY_TYPE_ID=38')  # Required count

# ODS
# curs.execute('SELECT * FROM ODS.ODS_IMS_BUSINESS ORDER BY IMS_ORG_ID LIMIT 10')
# curs.execute("SELECT COUNT(NAME) FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='ODS_IMS_BUSINESS'")
curs.execute("SELECT COUNT(NAME) FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='ODS_IMS_PROFESSIONAL'")
# curs.execute('SELECT * FROM ODS.ODS_PPD_FILE ORDER BY ME_NUMBER')
# curs.execute('SELECT * FROM ODS.ODS_PPD_FILE LIMIT 2')
# curs.execute('SELECT * FROM ODS.ODS_PPD_FILE ORDER BY ME_NUMBER LIMIT 11000, 1000')
# curs.execute("SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='ODS_PPD_FILE'")
# curs.execute('SELECT schemaname FROM syscat.schemata')
# curs.execute("SELECT * FROM SYSIBM.SYSTABLES WHERE CREATOR='AIMS'")
# curs.execute("SELECT CREATOR FROM SYSIBM.SYSTABLES WHERE CREATOR NOT LIKE 'SYS%' AND CREATOR NOT LIKE 'UNC%' AND CREATOR NOT LIKE 'UAC%' AND CREATOR NOT LIKE 'PI%' AND CREATOR NOT LIKE 'RDW%' AND CREATOR NOT LIKE 'DW%'")
# curs.execute("SELECT NAME FROM SYSIBM.SYSTABLES WHERE CREATOR='AMAEDW'")
# curs.execute("SELECT NAME FROM SYSIBM.SYSTABLES WHERE CREATOR='AMAEDW' AND NAME LIKE 'ENTITY%'")
results = curs.fetchall()
print(results)

# tables = ['ZIP_CITY_STATE_ZR', 'COUNTY_ZR', 'FONE_ZR', 'CENSUS_ZR', 'CBSA_ZR', 'MSA_ZR']
# queries = [
#     "SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='ZIP_CITY_STATE_ZR'",
#     "SELECT * FROM AMAEDW.ZIP_CITY_STATE_ZR LIMIT 2",
#     "SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='COUNTY_ZR'",
#     "SELECT * FROM AMAEDW.COUNTY_ZR LIMIT 2",
#     "SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='FONE_ZR'",
#     "SELECT * FROM AMAEDW.FONE_ZR LIMIT 2",
#     "SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='CENSUS_ZR'",
#     "SELECT * FROM AMAEDW.CENSUS_ZR LIMIT 2",
#     "SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='CBSA_ZR'",
#     "SELECT * FROM AMAEDW.CBSA_ZR LIMIT 2",
#     "SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='MSA_ZR'",
#     "SELECT * FROM AMAEDW.MSA_ZR LIMIT 2",
# ]
# for table in tables:
#     queries = [
#       f"SELECT NAME FROM SYSIBM.SYSCOLUMNS WHERE TBNAME='{table}'",
#       f"SELECT * FROM AMAEDW.{table} LIMIT 2"
#     ]
#
#     with open(f"{table}.csv", 'w') as file:
#         for query in queries:
#             curs.execute(query)
#             results = curs.fetchall()
#
#             if len(results[0]) == 1:
#                 # Header
#                 file.write(','.join(header[0] for header in results))
#                 file.write('\n')
#             else:
#                 # Data
#                 for row in results:
#                     file.write(','.join(str(value) for value in row))
#                     file.write('\n')
