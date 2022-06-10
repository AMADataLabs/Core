''' DAG definition for the Email Report ETL. '''
from   datalabs.etl.dag.dag import DAG

from   datalabs.etl.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.cpt.developer.transform import EmailReportGeneratorTask
from   datalabs.etl.orm.load import ORMLoaderTask


class EmailReportDAG(DAG):
    EXTRACT_EMAIL_REPORT: JDBCExtractorTask
    CREATE_EMAIL_REPORT: EmailReportGeneratorTask
    LOAD_EMAIL_REPORT: ORMLoaderTask


# pylint: disable=pointless-statement
EmailReportDAG.EXTRACT_EMAIL_REPORT \
    >> EmailReportDAG.CREATE_EMAIL_REPORT \
    >> EmailReportDAG.LOAD_EMAIL_REPORT
