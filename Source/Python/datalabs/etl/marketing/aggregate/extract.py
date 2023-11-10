"""Loader task for running marketing aggregator"""
from   dataclasses import dataclass
from   datetime import datetime
import json
import logging

import pandas

from   datalabs.access.atdata import AtData
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.marketing.aggregate.load import EmailValidationRequestLoaderTask
from   datalabs.etl.marketing.aggregate.transform import InputDataParser
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
class EmailValidationExtractorParameters:
    host: str
    account: str
    api_key: str
    execution_time: str
    max_months: int

# pylint: disable=line-too-long, protected-access
class EmailValidationExtractorTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = EmailValidationExtractorParameters

    def run(self):

        request_parameters = [
            json.loads(self._data[0].decode())["request_id"],
            json.loads(self._data[0].decode())["results_filename"]
        ]
        dated_dataset_with_emails = InputDataParser.parse(self._data[1])

        validated_emails = self._validate_emails(request_parameters)

        dated_dataset_with_emails = EmailValidationRequestLoaderTask._unset_update_flag_for_unexpired_emails(self, dated_dataset_with_emails)

        dated_dataset_with_emails = self._set_update_flag_for_valid_emails(dated_dataset_with_emails, validated_emails)

        dated_dataset_with_emails = self._remove_invalid_records(dated_dataset_with_emails)

        dated_dataset_with_emails = self._update_email_last_validated(dated_dataset_with_emails)

        validated_emails_results = pandas.DataFrame(data=dict(Emails=validated_emails))

        validation_results = [validated_emails_results, dated_dataset_with_emails]

        return [self._dataframe_to_csv(data) for data in validation_results]

    # pylint: disable=unused-variable
    def _validate_emails(self, request_parameters):
        status ='Processing'
        at_data = AtData(self._parameters.host, self._parameters.account, self._parameters.api_key)

        validated_emails = at_data.get_validation_results(request_parameters[0], request_parameters[1])

        return validated_emails

    # pylint: disable=unused-argument
    @classmethod
    def _set_update_flag_for_valid_emails(cls, dated_dataset_with_emails, validated_emails):
        dated_dataset_with_emails.loc[dated_dataset_with_emails.BEST_EMAIL.isin(validated_emails), 'update'] = True

        return dated_dataset_with_emails

    @classmethod
    def _remove_invalid_records(cls, dated_dataset_with_emails):
        return dated_dataset_with_emails[~dated_dataset_with_emails['update'].isnull()]

    # pylint: disable=singleton-comparison
    def _update_email_last_validated(self, dated_dataset_with_emails):
        dated_dataset_with_emails.loc[ dated_dataset_with_emails['update'] == True, 'email_last_validated'] = datetime.strptime(self._parameters.execution_time,'%Y-%m-%dT%H:%M:%S').strftime("%m/%d/%Y")

        return dated_dataset_with_emails
