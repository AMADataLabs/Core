""" JDBC Extractor """
from   dataclasses import dataclass
import logging
from   pathlib import Path
import string
import tempfile

import jaydebeapi
from   datalabs.etl.sql.extract import SQLExtractorTask, SQLParametricExtractorTask, SQLParquetExtractorTask

class JDBCConnectorMixin(SQLExtractorTask):

    def _connect(self):
        url = f"jdbc:{self._parameters.driver_type}://{self._parameters.database_host}:" \
              f"{self._parameters.database_port}"

        if self._parameters.database_name is not None:
            url += f"/{self._parameters.database_name}"

        if self._parameters.database_parameters is not None:
            url += f";{self._parameters.database_parameters}"

        connection = jaydebeapi.connect(
            self._parameters.driver,
            url,
            [self._parameters.database_username, self._parameters.database_password],
            self._parameters.jar_path.split(',')
        )
        
        return connection

class JDBCExtractorTask(JDBCConnectorMixin):
    pass

class JDBCParametricExtractorTask(SQLParametricExtractorTask):
    pass

class JDBCParquetExtractorTask(SQLParquetExtractorTask):
    pass
