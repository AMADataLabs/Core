import os

import jaydebeapi

from   datalabs.access.database import Database


class JDBC(Database):
    def __init__(self):
        self._connection = jaydebeapi.connect('com.ibm.db2.jcc.DB2Driver', 'jdbc:db2://server:port/database',
                                              [self._credentials.username, self._credentials.password])

    def connect(self):
        self._connection.execute('SET ISOLATION TO DIRTY READ;')