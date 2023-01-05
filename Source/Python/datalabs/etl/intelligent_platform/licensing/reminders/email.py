""" Licensing email reminder task """
from dataclasses import dataclass

from datalabs.messaging.email_message import send_email
from datalabs.parameter import add_schema
from datalabs.task import Task


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReminderEmailParameters:
    to: str  # pylint: disable=invalid-name
    cc: str = None  # pylint: disable=invalid-name
    execution_time: str = None


class ReminderEmailTask(Task):
    PARAMETER_CLASS = ReminderEmailParameters

    def run(self):
        email_addresses = self._csv_to_dataframe(self._data[0])[['email_id']].drop_duplicates()
        email_body_content = """<p>
                                Dear CPT® Development Licensee,                                
                                It has been 11 months into your 12 month license term. To maintain your access to the CPT code set for development purposes, you must complete a relicensing application. 

                                To extend your license, Sign in and complete the application <a href="https://compliance.ama-assn.org/hc/en-us/requests/new?ticket_form_id=1500000429302">here</a> 

                                Do not reply to this e-mail address. If you have questions, please contact us through the appropriate channel <a href="https://compliance.ama-assn.org/hc/en-us/articles/4411542991255">here</a>.

                                We hope that you will continue to use the CPT resources and will take this opportunity to provide us your <a href="https://platform.ama-assn.org/ama/#/feedback">feedback</a> on the CPT Developer Program.                                

                                Regards,            

                                AMA Staff
                                <b>NOTE: This message is being sent from a "Do Not Reply" address. Replies are NOT monitored.</b>                            </p> 
                            """

        for email_id in email_addresses['email_id']:
            send_email(
                to=email_id,
                subject=f'Reminder: Your CPT Development License is expiring - Sign in to extend your access',
                body=email_body_content,
                from_account='datalabs@ama-assn.org',
                html_content=True
            )


m
