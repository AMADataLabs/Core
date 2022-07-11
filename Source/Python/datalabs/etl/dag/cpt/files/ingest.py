''' DAG definition for CPT Files API Ingestion '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.s3.load import S3FileLoaderTask
from   datalabs.etl.sns.load import SNSMessageLoaderTask

class CPTFilesIngesterDAG(DAG):
    EXTRACT_LINK_ARCHIVE: S3FileExtractorTask
    LOAD_LINK_ARCHIVE: S3FileLoaderTask
    SCHEDULE_WATERMARK_DAG: "WatermarkDAGSchedulerTask"
    SCHEDULE_API_DAG: "APIDAGSchedulerTask"
    TRIGGER_WATERMARK_DAG: SNSMessageLoaderTask
    TRIGGER_API_DAG: SNSMessageLoaderTask

# pylint: disable=pointless-statement
CPTFilesIngesterDAG.EXTRACT_LINK_ARCHIVE >> CPTFilesIngesterDAG.LOAD_LINK_ARCHIVE
CPTFilesIngesterDAG.LOAD_LINK_ARCHIVE >> \
        CPTFilesIngesterDAG.SCHEDULE_WATERMARK_DAG >> CPTFilesIngesterDAG.TRIGGER_WATERMARK_DAG
CPTFilesIngesterDAG.LOAD_LINK_ARCHIVE >> \
        CPTFilesIngesterDAG.SCHEDULE_API_DAG >> CPTFilesIngesterDAG.TRIGGER_API_DAG
