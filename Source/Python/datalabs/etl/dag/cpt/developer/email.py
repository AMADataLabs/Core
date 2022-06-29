''' DAG definition for the Email Report ETL. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.cpt.developer.load import EmailReportSMTPLoaderTask

class EmailReportDAG(DAG):
    EXTRACT_EMAILS: "SQLExtractorTask"
    SEND_EMAIL_REPORT: EmailReportSMTPLoaderTask


# pylint: disable=pointless-statement
EmailReportDAG.EXTRACT_EMAILS \
    >> EmailReportDAG.SEND_EMAIL_REPORT
