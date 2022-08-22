''' AMC address flagging DAG definition. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.dag.cpt.cerner.transform import CernerReportTransformerTask


class CernerReportDAG(dag.DAG):
    EXTRACT_CERNER_DATA: JDBCExtractorTask
    LOAD_CERNER_REPORT: CernerReportTransformerTask

# pylint: disable=pointless-statement
CernerReportDAG.EXTRACT_CERNER_DATA >> CernerReportDAG.LOAD_CERNER_REPORT
