"""JDBC Extractor"""
import os

import jaydebeapi
import pandas

from datalabs.etl.extract import ExtractorTask
from datalabs.etl.task import ETLException


class JDBCExtractor(ExtractorTask):
    def _extract(self):
        dataframe = self._jdbc_connect()

        return dataframe

    def _jdbc_connect(self):
        url = 'jdbc:%s://%s:%s/%s' % ((self._parameters.variable['DRIVER_TYPE']), self._parameters.database['HOST'],
                                      self._parameters.database['PORT'], self._parameters.database['NAME'])
        ods = jaydebeapi.connect(self._parameters.variable['DRIVER'],
                                 url,
                                 [self._parameters.database['username'], self._parameters.database['password']],
                                 self.variables['JAR_PATH']
                                 )
        tables = self._read_queries_into_dataframe(ods)

        return tables

    def _read_queries_into_dataframe(self, ods):
        results = {}
        queries = self._split_queries(self._parameters.variable['SQL'])

        if all(query.split(' ')[0].lower() == 'select' for query in queries):
            for query in queries:
                results.update({query.split(' ')[3]: pandas.read_sql(query, ods)})

        return results

    @classmethod
    def _split_queries(cls, queries):
        queries_split = queries.split(';')
        queries_split.pop(len(queries_split) - 1)

        for i in range(len(queries_split)):
            queries_split[i] = queries_split[i].strip()

        return queries_split
