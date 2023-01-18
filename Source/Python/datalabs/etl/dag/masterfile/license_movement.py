''' DAG definition for License Movement Process '''
from   datalabs.analysis.ppma.license_movement.transform import LicenseMovementTransformerTask
from   datalabs.etl.dag import dag
from   datalabs.etl.dag.dag import register
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
from   datalabs.etl.sftp.load import SFTPFileLoaderTask
from   datalabs.etl.sql.extract import SQLExtractorTask


@register(name="LICENSE_MOVEMENT")
class DAG(dag.DAG):
    EXTRACT_PPD: SFTPFileExtractorTask
    EXTRACT_CREDENTIALING_ADDRESSES: SFTPFileExtractorTask
    EXTRACT_OLD_PPMA: SQLExtractorTask
    EXTRACT_MISMATCHES: SQLExtractorTask
    CREATE_BATCH_LOAD_FILE: LicenseMovementTransformerTask
    LOAD_BATCH_LOAD_FILE: SFTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_PPD >> DAG.CREATE_BATCH_LOAD_FILE
DAG.EXTRACT_CREDENTIALING_ADDRESSES >> DAG.CREATE_BATCH_LOAD_FILE
DAG.EXTRACT_OLD_PPMA >> DAG.CREATE_BATCH_LOAD_FILE
DAG.EXTRACT_MISMATCHES >> DAG.CREATE_BATCH_LOAD_FILE
DAG.CREATE_BATCH_LOAD_FILE >> DAG.LOAD_BATCH_LOAD_FILE