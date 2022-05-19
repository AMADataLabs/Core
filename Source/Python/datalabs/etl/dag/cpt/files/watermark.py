''' CPT files distribution watermarking DAG module '''
import datalabs.etl.dag.dag as dag
from   datalabs.etl.archive.transform import UnzipTransformerTask, ZipTransformerTask
from   datalabs.etl.control import DAGNotificationFactoryTask
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.pdf.transform import SignedPDFTransformerTask
from   datalabs.etl.sns.load import SNSMessageLoaderTask


class CoordinationDAG(dag.DAG):
    EXTRACT_USER_IDS: S3FileExtractorTask
    SCHEDULE_USER_DAGS: DAGNotificationFactoryTask
    NOTIFY_DAG_PROCESSOR: SNSMessageLoaderTask


class UserDAG(dag.DAG):
    EXTRACT_RELEASE_FILES: UnzipTransformerTask
    EXTRACT_SIGNING_CREDENTIALS: S3FileExtractorTask
    SIGN_PDFS: SignedPDFTransformerTask
    CREATE_WATERMARKED_DISTRIBUTION: ZipTransformerTask


# pylint: disable=pointless-statement

CoordinationDAG.EXTRACT_USER_IDS >> CoordinationDAG.SCHEDULE_USER_DAGS >> CoordinationDAG.NOTIFY_DAG_PROCESSOR


UserDAG.EXTRACT_SIGNING_CREDENTIALS >> UserDAG.SIGN_PDFS
UserDAG.EXTRACT_RELEASE_FILES >> UserDAG.SIGN_PDFS

UserDAG.SIGN_PDFS >> UserDAG.CREATE_WATERMARKED_DISTRIBUTION
