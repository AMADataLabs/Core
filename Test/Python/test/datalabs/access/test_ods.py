""" source: datalabs.access.ods """
import os

import jaydebeapi
import pytest
import sqlalchemy as sa


@pytest.mark.skip(reason="Example JDBC Usage")
def test_jdbc_connction():
    """ Prerequsites:
            JDK: sudo apt install default-jre
            jaydebeapi: pip install jaydebeapi
            DB2 JDBC Driver: Put db2jcc4.jar in run directory (download from https://dbschema.com/jdbc-driver/Db2.html).
    """
    ods = jaydebeapi.connect(
        'com.ibm.db2.jcc.DB2Jcc',
        'jdbc:db2://rdbp1190.ama-assn.org:54150/eprdods',
        [os.getenv('DATABASE_ODS_USERNAME'), os.getenv('DATABASE_ODS_PASSWORD')],
        './db2jcc4.jar'
    )

    curs = ods.cursor()
    # curs.execute('select schemaname from syscat.schemata')
    # curs.execute("select name from sysibm.systables where type='T' and creator='ODS'")
    curs.execute('select * from ODS.ODS_PPD_FILE LIMIT 10')

    results = curs.fetchall()

    print(results)
    assert False


@pytest.mark.skip(reason="Example SQLAlchemy Usage")
def test_sqlalchemy_connection():
    username = os.getenv('DATABASE_ODS_USERNAME')
    password = os.getenv('DATABASE_ODS_PASSWORD')
    engine = sa.create_engine(f"ibmi://{username}:{password}@rdbp1190.ama-assn.org:54150/eprdods")
    connection = engine.connect()
    metadata = sa.MetaData()

    query = connection.execute("select * from ODS.ODS_PPD_FILE LIMIT 10")
    result = query.fetchall()

    print(result)
