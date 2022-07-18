''' DAG definition for CPT Files API Ingestion '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.s3.load import S3FileLoaderTask
from   datalabs.etl.sns.load import SNSMessageLoaderTask

class CPTFilesIngestionDAG(DAG):
    LOAD_FILES_ARCHIVE: S3FileLoaderTask
    SCHEDULE_WATERMARK_DAG: "WatermarkDAGSchedulerTask"
    SCHEDULE_API_DAG: "APIDAGSchedulerTask"
    TRIGGER_WATERMARK_DAG: SNSMessageLoaderTask
    TRIGGER_API_DAG: SNSMessageLoaderTask

# pylint: disable=pointless-statement
CPTFilesIngestionDAG.LOAD_FILES_ARCHIVE >> \
        CPTFilesIngestionDAG.SCHEDULE_WATERMARK_DAG >> CPTFilesIngestionDAG.TRIGGER_WATERMARK_DAG
CPTFilesIngestionDAG.LOAD_FILES_ARCHIVE >> \
        CPTFilesIngestionDAG.SCHEDULE_API_DAG >> CPTFilesIngestionDAG.TRIGGER_API_DAG
