''' AMC address flagging DAG definition. '''
from   datalabs.analysis.amc.transform import AMCAddressFlaggingTransformerTask
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.jdbc.extract import JDBCExtractorTask
from   datalabs.analysis.amc.load import AMCReportSMTPLoaderTask


class DAG(dag.DAG):
    EXTRACT_AMC: JDBCExtractorTask
    FLAG_ADDRESSES: AMCAddressFlaggingTransformerTask
    EMAIL_ADDRESS_REPORT: AMCReportSMTPLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_AMC >> DAG.FLAG_ADDRESSES >> DAG.EMAIL_ADDRESS_REPORT
