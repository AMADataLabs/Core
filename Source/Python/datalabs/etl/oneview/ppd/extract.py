""" Oneview PPD Extractor from ods"""
import pandas
import settings

from   datalabs.access.ods import ODS
from   datalabs.etl.extract import ExtractorTask
from   datalabs.etl.task import ETLException


class PPDExtractorODS(ODS, ExtractorTask):
    def __init__(self):
        self.query = '''SELECT * FROM ODS.ODS_PPD_FILE PE'''

    def _extract(self):
        with ODS() as ods:
            ppd = ods.read(self.query)

        return ppd
