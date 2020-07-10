""" CPT ETL Transformer classes """
from   dataclasses import dataclass
from   datetime import datetime
import io
import logging

import pandas

from   datalabs.etl.s3.cpt.api.load import CPTRelationalTableLoader
from   datalabs.etl.s3.cpt.api.transform import CSVToRelationalTablesTransformer
from   datalabs.etl.s3.extract import S3WindowsTextExtractor
from   datalabs.etl.task import ETLTask, ETLException
from   datalabs.etl.transform import Transformer

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class LoadAPIDatabaseETLTask(ETLTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self.set_extractor(S3WindowsTextExtractor)
        self.set_transformer(CSVToRelationalTablesTransformer)
        self.set_loader(CPTRelationalTableLoader)
