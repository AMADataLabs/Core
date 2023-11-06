"""Loader task for running marketing aggregator"""
from   dataclasses import dataclass
from   datetime import datetime
import json
import logging

import pandas

from   datalabs.access.atdata import AtData
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.marketing.aggregate.transform import InputDataParser
from   datalabs.etl.task import ExecutionTimeMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
class EmailValidationRequestLoaderParameters:
    host: str
    account: str
    api_key: str
    execution_time: str
    max_months: int
    left_merge_key: str
    right_merge_key: str

# pylint: disable=consider-using-with, line-too-long
class EmailValidationRequestLoaderTask(ExecutionTimeMixin, CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = EmailValidationRequestLoaderParameters

    def run(self):
        dataset_with_emails, dataset_with_validation_dates = [InputDataParser.parse(x) for x in self._data]

        dated_dataset_with_emails = self._add_existing_validation_dates_to_emails(dataset_with_emails, dataset_with_validation_dates)

        dated_dataset_with_emails = self._calculate_months_since_last_validated(dated_dataset_with_emails)

        request_parameters = self._validate_expired_records(dated_dataset_with_emails)

        request_parameters = self._create_request_parameters_dict(request_parameters)

        return [
            json.dumps(request_parameters).encode(),
            self._dataframe_to_csv(dated_dataset_with_emails)
        ]

    def _add_existing_validation_dates_to_emails(self, dataset_with_emails, dataset_with_validation_dates):
        if not dataset_with_validation_dates[self._parameters.right_merge_key].is_unique:
            dataset_with_validation_dates = self._remove_duplicate_dataset_with_validation_dates(dataset_with_validation_dates)

        data = dataset_with_emails.merge(dataset_with_validation_dates, left_on=self._parameters.left_merge_key, right_on=self._parameters.right_merge_key, how='left')

        data['email_last_validated'] = data.groupby(['BEST_EMAIL'], sort=False)['email_last_validated'].apply(lambda x: x.ffill())

        return data

    def _calculate_months_since_last_validated(self, dated_dataset_with_emails):
        execution_time = datetime.strptime(self._parameters.execution_time, '%Y-%m-%dT%H:%M:%S')

        dated_dataset_with_emails["months_since_validated"] = (execution_time - pandas.to_datetime(dated_dataset_with_emails.email_last_validated[~dated_dataset_with_emails.email_last_validated.isnull()])).astype('timedelta64[M]')

        dated_dataset_with_emails.months_since_validated[dated_dataset_with_emails.email_last_validated.isnull()] = 6

        return dated_dataset_with_emails

    # pylint: disable=no-member, no-value-for-parameter
    def _validate_expired_records(self, dated_dataset_with_emails):
        dated_dataset_with_emails = self._unset_update_flag_for_unexpired_emails(dated_dataset_with_emails)

        email_data_list = self._get_expired_emails(dated_dataset_with_emails)

        request_parameters = self._validate_emails(email_data_list)

        return request_parameters

    @classmethod
    def _create_request_parameters_dict(cls, request_parameters):
        request_parameters_dict = {}

        if len(request_parameters) != 0:
            request_parameters_dict = dict(
                request_id=request_parameters[0],
                results_filename=request_parameters[1]
            )

        return request_parameters_dict

    @classmethod
    def _remove_duplicate_dataset_with_validation_dates(cls, dataset_with_validation_dates):
        return dataset_with_validation_dates[['BEST_EMAIL', 'email_last_validated']].drop_duplicates()

    def _unset_update_flag_for_unexpired_emails(self, dated_dataset_with_emails):
        mask =  dated_dataset_with_emails.months_since_validated.astype('float') < float(self._parameters.max_months)

        dated_dataset_with_emails.loc[mask, 'update'] = False

        dated_dataset_with_emails.loc[(~mask & ~dated_dataset_with_emails.BEST_EMAIL.isnull()), 'update'] = True

        return dated_dataset_with_emails

    # pylint: disable=singleton-comparison
    @classmethod
    def _get_expired_emails(cls, dated_dataset_with_emails):
        expired_emails = list(set(dated_dataset_with_emails[dated_dataset_with_emails['update'] == True].BEST_EMAIL.values))

        return expired_emails

    # pylint: disable=unused-variable
    def _validate_emails(self, email_data_list):
        status ='Processing'
        request_id, file = None, None

        at_data = AtData(self._parameters.host, self._parameters.account, self._parameters.api_key)

        request_id = at_data.request_email_validation(email_data_list)

        return [request_id, file]
