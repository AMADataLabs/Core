from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.dag.schedule import DAGSchedulerTask
from   datalabs.etl.s3.extract import S3FileExtractorTask

class DAGSchedulerDAG(DAG):
    EXTRACT_SCHEDULE: S3FileExtractorTask
    SCHEDULE_DAGS: DAGSchedulerTask


DAGSchedulerDAG.EXTRACT_SCHEDULE >> DAGSchedulerDAG.SCHEDULE_DAGS
