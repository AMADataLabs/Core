""" DBL report email loader task class """

from dataclasses import dataclass
from datetime import datetime
import pickle as pk

# pylint: disable=import-error
from datalabs.etl.load import LoaderTask
from datalabs.messaging.email_message import send_email, Attachment
from datalabs.parameter import add_schema


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes, invalid-name
class DBLReportEmailLoaderParameters:
    to: str
    cc: str
    fail_to: str
    fail_cc: str
    data: list
    execution_time: str = None


class DBLReportEmailLoaderTask(LoaderTask):
    PARAMETER_CLASS = DBLReportEmailLoaderParameters

    def _load(self):
        today = str(datetime.now().date())
        subject = f'Weekly DBL Report - {today}'
        attachment = Attachment(subject + '.xlsx', data=self._parameters.data[0])
        previous_report = Attachment('Previous DBL Report.xlsx', data=self._parameters.data[1])
        validation_results = pk.loads(self._parameters.data[2])

        passing = validation_results['Passing']
        log = validation_results['Log']
        # tab_validations = validation_results['Validations']

        if passing:
            to = self._parameters.to
            cc = self._parameters.cc
            body = 'Attached is the auto-generated DBL report file.'
            attachments = [attachment]

        else:  # failing validation
            to = self._parameters.fail_to
            cc = self._parameters.fail_cc
            subject = subject + '--- VALIDATION FAILED'
            body = f"The auto-generated DBL report file has FAILED validation checks. See details below:\n"\
                   f"{'~'*40}\n"\
                   f"{log}"\
                   f"{'~'*40}\n"\
                   f"Please determine the cause of the error by comparing the attached DBL reports\n"\
                   f"and forward info to Garrett Lappe for any required changes to the validation process.\n"

            attachments = [attachment, previous_report]

        send_email(
            to=to,
            cc=cc,
            subject=subject,
            body=body,
            from_account='datalabs@ama-assn.org',
            attachments=attachments
        )
