""" DBL report email loader task class """
from   dataclasses import dataclass
from   datetime import datetime
import pickle as pk

from   datalabs.messaging.email_message import send_email, Attachment
from   datalabs.parameter import add_schema
from   datalabs.task import Task


@add_schema
@dataclass
class DBLReportEmailLoaderParameters:
    to: str  # pylint: disable=invalid-name
    cc: str  # pylint: disable=invalid-name
    fail_to: str
    fail_cc: str
    execution_time: str = None


class DBLReportEmailLoaderTask(Task):
    PARAMETER_CLASS = DBLReportEmailLoaderParameters

    def run(self):
        today = str(datetime.now().date())
        subject = f'Weekly DBL Report - {today}'
        attachment = Attachment(subject + '.xlsx', data=self._data[0])
        previous_report = Attachment('Previous DBL Report.xlsx', data=self._data[1])
        validation_results = pk.loads(self._data[2])
        to_emails = self._parameters.to
        cc_emails = self._parameters.cc
        body = 'Attached is the auto-generated DBL report file.'

        passing = validation_results['Passing']
        log = validation_results['Log']
        # tab_validations = validation_results['Validations']

        if not passing:  # failing validation
            to_emails = self._parameters.fail_to
            cc_emails = self._parameters.fail_cc
            subject = subject + '--- VALIDATION FAILED'
            body = f"The auto-generated DBL report file has FAILED validation checks. See details below:\n"\
                   f"{'~'*40}\n"\
                   f"{log}"\
                   f"{'~'*40}\n"\
                   f"Please determine the cause of the error by comparing the attached DBL reports\n"\
                   f"and forward info to Garrett Lappe for any required changes to the validation process.\n"

        send_email(
            to=to_emails,
            cc=cc_emails,
            subject=subject,
            body=body,
            from_account='datalabs@ama-assn.org',
            attachments=[attachment, previous_report]
        )
