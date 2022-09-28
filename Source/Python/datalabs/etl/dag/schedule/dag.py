''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG, register
from   datalabs.etl.schedule.transform import DAGSchedulerTask
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.sns.load import SNSMessageLoaderTask


@register(name="DAG_SCHEDULER")
class DAGSchedulerDAG(DAG):
    __name__
    EXTRACT_SCHEDULE: S3FileExtractorTask
    SCHEDULE_DAGS: DAGSchedulerTask
    NOTIFY_DAG_PROCESSOR: SNSMessageLoaderTask


# pylint: disable=pointless-statement
DAGSchedulerDAG.EXTRACT_SCHEDULE >> DAGSchedulerDAG.SCHEDULE_DAGS >> DAGSchedulerDAG.NOTIFY_DAG_PROCESSOR
