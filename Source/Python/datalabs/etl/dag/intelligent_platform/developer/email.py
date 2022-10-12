''' DAG definition for the Email Report ETL. '''
import datalabs.etl.dag.dag as dag
from   datalabs.etl.cpt.developer.load import EmailReportSMTPLoaderTask


@dag.register(name="DEVELOPER_EMAILS")
class DAG(dag.DAG):
    EXTRACT_EMAILS: "SQLExtractorTask"
    SEND_EMAIL_REPORT: EmailReportSMTPLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_EMAILS >> DAG.SEND_EMAIL_REPORT
