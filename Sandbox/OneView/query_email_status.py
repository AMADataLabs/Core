import os

import jaydebeapi

aims = jaydebeapi.connect(
  'com.ibm.db2.jcc.DB2Jcc',
  'jdbc:db2://rdbp1190.ama-assn.org:54000/prddw',
  [os.getenv('JDBC_USERNAME'), os.getenv('JDBC_PASSWORD')],
  ['./db2jcc4.jar']
)

'''
    ONEVIEW__EXTRACT_PHYSICIAN_EMAIL__SQL: "SELECT EMAIL_ID, EMAIL_STATUS FROM AMAEDW.EMAIL_ADDR;"
    ONEVIEW__EXTRACT_PHYSICIAN_EMAIL_ID__SQL: "SELECT PARTY_ID, EMAIL_ID FROM AMAEDW.PARTY_EMAIL;"
'''
query = '''
SELECT party.PARTY_ID as me, addr.EMAIL_STATUS as status FROM AMAEDW.EMAIL_ADDR addr
INNER JOIN AMAEDW.PARTY_EMAIL party
ON party.EMAIL_ID=addr.EMAIL_ID
ORDER BY me
LIMIT 10000000, 1000000
'''
# LIMIT 10000000, 1000000
# SELECT count(party.PARTY_ID) FROM AMAEDW.EMAIL_ADDR addr
# INNER JOIN AMAEDW.PARTY_EMAIL party
# ON party.EMAIL_ID=addr.EMAIL_ID
# '''
# SELECT party.PARTY_ID as me, addr.EMAIL_STATUS as status FROM AMAEDW.EMAIL_ADDR addr
# INNER JOIN AMAEDW.PARTY_EMAIL party
# ON party.EMAIL_ID=addr.EMAIL_ID
# ORDER BY me
# LIMIT 10
# '''
curs = aims.cursor()
curs.execute(query)
results = curs.fetchall()
print(results)
