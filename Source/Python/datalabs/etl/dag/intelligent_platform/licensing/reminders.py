''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.smtp.load import SMTPFileLoaderTask
from   datalabs.etl.orm.load import ORMLoaderTask


@dag.register(name="LICENSING_TRAFFIC")
class DAG(dag.DAG):
    EXTRACT_EMAILS: SQLAlchemyExtractorTask
    SEND_REMINDER_EMAIL: SMTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_EMAILS >> DAG.SEND_REMINDER_EMAIL


# pylint: disable=pointless-statement
