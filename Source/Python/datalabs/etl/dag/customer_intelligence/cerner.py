''' AMC address flagging DAG definition. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.smtp.load import SMTPFileLoaderTask


@dag.register(name="CERNER_REPORT")
class DAG(dag.DAG):
    EXTRACT_CERNER_DATA: SQLAlchemyExtractorTask
    LOAD_CERNER_REPORT: SMTPFileLoaderTask

# pylint: disable=pointless-statement
DAG.EXTRACT_CERNER_DATA >> DAG.SEND_CERNER_REPORT
