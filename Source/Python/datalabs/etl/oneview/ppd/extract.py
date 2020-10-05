""" Oneview PPD Extractor from ods"""
import jaydebeapi
import pandas

import settings

from   datalabs.access.jdbc import JDBC
from   datalabs.etl.extract import ExtractorTask
from   datalabs.etl.task import ETLException


class PPDExtractorODS(JDBC, ExtractorTask):
    def __init__(self):
        self.query = '''SELECT * FROM ODS.ODS_PPD_FILE PE'''

    def _extract(self):
        with JDBC() as jdbc:
            ppd = jdbc.read(self.query)

        return ppd
