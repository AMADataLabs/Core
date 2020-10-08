"""JDBC Extractor into"""
import os

import jaydebeapi
import pandas


class JDBCExtractor:
    def __init__(self):
        self.query = os.environ['EXTRACTOR_SQL']
        self.username = os.environ['DATABASE_ODS_USERNAME']
        self.password = os.environ['DATABASE_ODS_PASSWORD']

    def _jdbc_connect(self):
        ods = jaydebeapi.connect(
            'com.ibm.db2.jcc.DB2Jcc',
            'jdbc:db2://rdbp1190.ama-assn.org:54150/eprdods',
            [self.username, self.password],
        )
        tables = self._read_queries_into_dataframe(ods)

        return tables

    def _read_queries_into_dataframe(self, ods):
        results = {}
        queries = self._split_queries(self.query)

        if all(query.split(' ')[0].lower() == 'select' for query in queries):
            for query in queries:
                results.update({query.split(' ')[3]: pandas.read_sql(self.query, ods)})

        return results

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')
        queries_split.pop(len(queries_split) - 1)

        for i in range(len(queries_split)):
            queries_split[i] = queries_split[i].strip()

        return queries_split
