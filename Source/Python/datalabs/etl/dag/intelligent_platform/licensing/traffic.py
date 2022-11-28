''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.smtp.load import SMTPFileLoaderTask
from   datalabs.etl.orm.load import ORMLoaderTask

@dag.register(name="LICENSING_TRAFFIC")
class DAG(dag.DAG):
    EXTRACT_TRAFFIC: SQLAlchemyExtractorTask
    SEND_TRAFFIC_REPORT: SMTPFileLoaderTask
    EXTRACT_COUNTS: SQLAlchemyExtractorTask
    LOAD_COUNTS_TABLE: ORMLoaderTask
    SEND_APPLICANT_DATA: SMTPFileLoaderTask

# pylint: disable=pointless-statement
DAG.EXTRACT_TRAFFIC >> DAG.SEND_TRAFFIC_REPORT
DAG.EXTRACT_COUNTS >> DAG.LOAD_COUNTS_TABLE
DAG.EXTRACT_COUNTS >> DAG.SEND_APPLICANT_DATA


# pylint: disable=pointless-statement
