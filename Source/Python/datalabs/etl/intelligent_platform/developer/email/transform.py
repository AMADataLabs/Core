""" Transformer to convert raw CPT licensed organizations list to a curated organization list for
frictionless licensing front-end validation"""
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
class EmailTransformerParameters:
    execution_time: str = None
    data: object = None


class EmailReportGeneratorTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = EmailTransformerParameters

    def run(self):
        pass
