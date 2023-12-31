import os

import jaydebeapi

aims = jaydebeapi.connect(
  'com.ibm.db2.jcc.DB2Jcc',
  'jdbc:db2://rdbp1190.ama-assn.org:54150/eprdods',
  ['dlabs', os.getenv('JDBC_PASSWORD')],
  ['./db2jcc4.jar']
)

query = \
'''
SELECT count(B.IMS_ORG_ID) FROM ODS.ODS_IMS_BUSINESS B
'''
'''1022856'''
'''
SELECT B.IMS_ORG_ID, B.BUSINESS_NAME, B.DBA_NAME, B.ADDRESS_ID, B.PHYSICAL_ADDR_1, B.PHYSICAL_ADDR_2, B.PHYSICAL_CITY, B.PHYSICAL_STATE, B.PHYSICAL_ZIP, B.POSTAL_ADDR_1, B.POSTAL_ADDR_2, B.POSTAL_CITY, B.POSTAL_STATE, B.POSTAL_ZIP, B.PHONE, B.FAX, B.WEBSITE, B.LATITUDE, B.LONGITUDE, B.OWNER_STATUS, B.PROFIT_STATUS, B.PRIMARY_COT_ID, B.COT_CLASSIFICATION_ID, B.COT_CLASSIFICATION, B.COT_FACILITY_TYPE_ID, B.COT_FACILITY_TYPE, B.COT_SPECIALTY_ID, B.COT_SPECIALTY, B.RECORD_TYPE, B.TTL_LICENSE_BEDS, B.TTL_CENSUS_BEDS, B.TTL_STAFFED_BEDS, B.TEACHING_HOSP, B.COMMHOSP, B.MSA, B.FIPS_STATE, B.FIPS_COUNTY, B.NUM_OF_PROVIDERS, B.ELECTRONIC_MED_REC, B.EPRESCRIBE, B.PAYPERFORM, B.DEACTIVATION_REASON, B.REFERBACK_IMS_ORG_ID, B.STATUS_INDICATOR, B.BATCH_BUSINESS_DATE FROM ODS.ODS_IMS_BUSINESS B ORDER BY B.IMS_ORG_ID
LIMIT 0, 1000000
'''
curs = aims.cursor()
curs.execute(query)
results = curs.fetchall()
print(results)
