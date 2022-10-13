''' DAG definition for the Email Report ETL. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.intelligent_platform.developer.email.load import EmailReportSMTPLoaderTask
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask


@dag.register(name="DEVELOPER_EMAILS")
class DAG(dag.DAG):
    EXTRACT_EMAILS: SQLAlchemyExtractorTask
    SEND_EMAIL_REPORT: EmailReportSMTPLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_EMAILS >> DAG.SEND_EMAIL_REPORT
