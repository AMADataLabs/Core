''' DBL counts report DAG definition. '''
from   datalabs.analysis.dbl.load import DBLReportEmailLoaderTask
from   datalabs.analysis.dbl.transform import DBLReportTransformer
import datalabs.etl.dag.dag as dag
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
from   datalabs.etl.sftp.load import SFTPFileLoaderTask


class DAG(dag.DAG):
    EXTRACT_DBL: SFTPFileExtractorTask
    GET_LAST_REPORT: SFTPFileExtractorTask
    CREATE_DBL_REPORT: DBLReportTransformer
    EMAIL_DBL_REPORT: DBLReportEmailLoaderTask
    LOAD_DBL_REPORT: SFTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_DBL >> DAG.CREATE_DBL_REPORT
DAG.GET_LAST_REPORT >> DAG.CREATE_DBL_REPORT
DAG.CREATE_DBL_REPORT >> DAG.EMAIL_DBL_REPORT
DAG.CREATE_DBL_REPORT >> DAG.LOAD_DBL_REPORT
