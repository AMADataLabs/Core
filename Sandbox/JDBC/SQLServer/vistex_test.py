import os

import jaydebeapi

database = jaydebeapi.connect(
  'com.microsoft.sqlserver.jdbc.SQLServerDriver',
  # 'jdbc:sqlserver://rdbp5323.ad.ama-assn.org:1433;databaseName=LicenseMaestro_CPT;encrypt=true;trustServerCertificate=true',
  'jdbc:sqlserver://rdbp5323.ad.ama-assn.org:1433;databaseName=AMA_LicensePortal;encrypt=true;trustServerCertificate=true',
  [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
  './sqljdbc_10.2/mssql-jdbc-10.2.0.jre8.jar'
)
# jdbc:sqlserver://localhost:1433;databaseName=AdventureWorks;user=MyUserName;password=*****;
curs = database.cursor()
# curs.execute('SELECT name, database_id, create_date FROM sys.databases;')
# curs.execute('SELECT name, schema FROM SYSOBJECTS;')
# curs.execute('SELECT * FROM INFORMATION_SCHEMA.TABLES;')
# curs.execute('exec dbo.usp_DistributionDownloadExclusions;')
curs.execute('SELECT TOP 10 * FROM dbo.InternalUseContentDownloads_ActivityLog;')
# InternalUseContentDownloads_ActivityLog
results = curs.fetchall()

print(results)
