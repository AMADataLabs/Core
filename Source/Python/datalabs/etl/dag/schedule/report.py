''' DAG Report definition. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.schedule.transform import DAGSchedulerTask
from   datalabs.etl.smtp.load import SMTPFileLoaderTask


@dag.register(name="DAG_REPORT")
class DAG(dag.DAG):
    EXTRACT_SCHEDULE: S3FileExtractorTask
    IDENTIFY_SCHEDULED_DAGS: DAGSchedulerTask
    EXTRACT_SCHEDULED_DAG_STATES: DAGSchedulerTask
    SEND_DAG_REPORT: SMTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_SCHEDULE \
        >> DAG.IDENTIFY_SCHEDULED_DAGS \
        >> DAG.EXTRACT_SCHEDULED_DAG_STATES \
        >> DAG.SEND_DAG_REPORT
