''' DAG definition for CPT Files API Ingestion '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.archive.transform import UnzipTransformerTask
from   datalabs.etl.s3.load import S3FileLoaderTask
from   datalabs.etl.sns.load import SNSMessageLoaderTask

class CPTFilesIngesterDAG(DAG):
    EXTRACT_SCHEDULE: S3FileExtractorTask
    LOAD_SCHEDULE: S3FileLoaderTask
    UNZIP_HCPCS_REPORTS: UnzipTransformerTask
    NOTIFY_DAG_PROCESSOR: SNSMessageLoaderTask

# pylint: disable=pointless-statement
CPTFilesIngesterDAG.EXTRACT_SCHEDULE >> CPTFilesIngesterDAG.LOAD_SCHEDULE >> \
        CPTFilesIngesterDAG.UNZIP_HCPCS_REPORTS >> CPTFilesIngesterDAG.NOTIFY_DAG_PROCESSOR
