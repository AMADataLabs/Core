""" Licensing email reminder task """
from dataclasses import dataclass

from datalabs.messaging.email_message import send_email
from datalabs.parameter import add_schema
from datalabs.task import Task

from datalabs.etl.csv import CSVReaderMixin


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReminderEmailParameters:
    platform_domain: str
    execution_time: str = None


class ReminderEmailTask(CSVReaderMixin, Task):
    PARAMETER_CLASS = ReminderEmailParameters

    def run(self):
        email_addresses = self._csv_to_dataframe(self._data[0])[['email_id']].drop_duplicates()
        platform_url = f"https://{self._parameters.platform_domain}.ama-assn.org/ama/#"

        email_body_content = \
            f"""<p>
                Dear CPT® Development Licensee,</p>
                <p>It has been 11 months into your 12 month license term. To maintain your access to the CPT code set
                for development purposes, you must complete a relicensing application.</p>

                <p>To extend your license, Sign in and complete the application
                <a href="{platform_url}/fll?dl_renew=true">here</a>
                </p>

                <p>Do not reply to this e-mail address. If you have questions, please contact us through the appropriate
                channel <a href="https://compliance.ama-assn.org/hc/en-us/articles/4411542991255">here</a>.</p>

                <p>We hope that you will continue to use the CPT resources and will take this opportunity to provide us
                your <a href="{platform_url}/feedback">feedback</a> on the CPT Developer Program.
                </p>

                <p>Regards,</p>

                <p>AMA Staff</p>
                <p><b>NOTE: This message is being sent from a "Do Not Reply" address. Replies are NOT monitored.</b>
                </p>
            """

        for email_id in email_addresses['email_id']:
            send_email(
                to=email_id,
                subject='Reminder: Your CPT Development License is expiring - Sign in to extend your access',
                from_account='platform@ama-assn.org',
                html_content=email_body_content
            )
