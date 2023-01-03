''' DAG definition for the Intelligent Platform Licensing ETL. '''
from datalabs.etl.dag import dag
from datalabs.etl.smtp.load import SMTPFileLoaderTask
from datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask

from Source.Python.datalabs.etl.intelligent_platform.licensing.reminders.get_reminders import GetRemindersTask
from Source.Python.datalabs.etl.intelligent_platform.licensing.reminders.update_reminders import UpdateRemindersTask


@dag.register(name="LICENSING_TRAFFIC")
class DAG(dag.DAG):
    EXTRACT_EMAILS: SQLAlchemyExtractorTask
    SEND_REMINDER_EMAIL: SMTPFileLoaderTask
    GET_REMINDER_COUNTS: GetRemindersTask
    UPDATE_REMINDER_COUNTS: UpdateRemindersTask


# pylint: disable=pointless-statement
DAG.EXTRACT_EMAILS >> DAG.SEND_REMINDER_EMAIL
DAG.SEND_REMINDER_EMAIL >> DAG.GET_REMINDER_COUNTS
DAG.GET_REMINDER_COUNTS >> DAG.UPDATE_REMINDER_COUNTS
# pylint: disable=pointless-statement
