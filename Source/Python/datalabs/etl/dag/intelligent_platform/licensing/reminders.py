''' DAG definition for the Intelligent Platform Licensing ETL. '''
from datalabs.etl.dag import dag
from datalabs.etl.intelligent_platform.licensing.reminders.email import ReminderEmailTask
from datalabs.etl.intelligent_platform.licensing.reminders.update_reminders import IncrementRemindersTask
from datalabs.etl.orm.load import ORMLoaderTask
from datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask

@dag.register(name="LICENSING_REMINDERS")
class DAG(dag.DAG):
    EXTRACT_EMAILS: SQLAlchemyExtractorTask
    SEND_REMINDER_EMAILS: ReminderEmailTask
    INCREMENT_REMINDER_COUNTS: IncrementRemindersTask
    UPDATE_GROUPS_TABLE: ORMLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_EMAILS >> DAG.SEND_REMINDER_EMAILS
DAG.SEND_REMINDER_EMAILS >> DAG.INCREMENT_REMINDER_COUNTS
DAG.INCREMENT_REMINDER_COUNTS >> DAG.UPDATE_GROUPS_TABLE
