from   abc import abstractmethod
from   collections import defaultdict
import json
import logging
import os

from   datalabs.etl.cpt.ingest.extract import CPTTextDataExtractor
from   datalabs.etl.cpt.ingest.transform import CPTFileToCSVTransformer
from   datalabs.etl.s3.load import S3WindowsTextLoader
from   datalabs.etl.task import ETLTask, ETLException
from   datalabs.etl.transform import Transformer
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ConvertRawDataETLTaskTask(ETLTask):
    def __init__(self, parameters):
        super().__init__(parameters)

        self.set_extractor(CPTTextDataExtractor)
        self.set_transformer(CPTFileToCSVTransformer)
        self.set_loader(S3WindowsTextLoader)
