""" Extract emails validation results from AtData API . """
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.marketing.aggregate.transform import InputDataParser
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class EmailValidationExtractorTaskParameters:
    execution_time: str = None

class EmailValidationExtractorTask(Task, ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin):
    PARAMETER_CLASS = EmailValidationExtractorTaskParameters

    def run(self):
        validated_emails = InputDataParser.parse(self._data[0])
        LOGGER.info("Validated Emails:\n%s", validated_emails)

        return [self._dataframe_to_csv(validated_emails)]
