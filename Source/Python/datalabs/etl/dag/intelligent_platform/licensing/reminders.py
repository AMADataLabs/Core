''' DAG definition for the Intelligent Platform Licensing ETL. '''
from datalabs.etl.dag import dag
from datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask

from datalabs.etl.dag import PythonTask
from datalabs.etl.intelligent_platform.licensing.reminders.email import ReminderEmailTask
from datalabs.etl.intelligent_platform.licensing.reminders.update_reminders import UpdateRemindersTask


@dag.register(name="LICENSING_TRAFFIC")
class DAG(dag.DAG):
    EXTRACT_EMAILS: SQLAlchemyExtractorTask
    SEND_REMINDER_EMAILS: ReminderEmailTask
    INCREMENT_REMINDER_COUNTS: UpdateRemindersTask
    UPDATE_GROUPS_TABLE: PythonTask("datalabs.etl.orm.load.ORMLoaderTask")


# pylint: disable=pointless-statement
DAG.EXTRACT_EMAILS >> DAG.SEND_REMINDER_EMAILS
DAG.SEND_REMINDER_EMAILS >> DAG.EXTRACT_REMINDER_COUNTS
DAG.EXTRACT_REMINDER_COUNTS >> DAG.UPDATE_REMINDER_COUNTS
