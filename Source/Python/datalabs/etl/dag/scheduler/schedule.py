''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.dag.schedule import DAGSchedulerTask
from   datalabs.etl.s3.extract import S3FileExtractorTask

class DAGSchedulerDAG(DAG):
    EXTRACT_SCHEDULE: S3FileExtractorTask
    SCHEDULE_DAGS: DAGSchedulerTask
    NOTIFY_DAG_PROCESSOR: DAGSchedulerTask


# pylint: disable=pointless-statement
DAGSchedulerDAG.EXTRACT_SCHEDULE >> DAGSchedulerDAG.SCHEDULE_DAGS >> DAGSchedulerDAG.NOTIFY_DAG_PROCESSOR
