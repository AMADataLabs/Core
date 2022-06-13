''' DAG definition for the Email Report ETL. '''
from   datalabs.etl.dag.dag import DAG

from   datalabs.etl.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.cpt.developer.transform import EmailReportGeneratorTask
from   datalabs.etl.cpt.developer.load import EmailReportSMTPLoaderTask

class EmailReportDAG(DAG):
    EXTRACT_EMAILS: JDBCExtractorTask
    CREATE_EMAIL_REPORT: EmailReportGeneratorTask
    SEND_EMAIL_REPORT: EmailReportSMTPLoaderTask


# pylint: disable=pointless-statement
EmailReportDAG.EXTRACT_EMAILS \
    >> EmailReportDAG.CREATE_EMAIL_REPORT \
    >> EmailReportDAG.SEND_EMAIL_REPORT
