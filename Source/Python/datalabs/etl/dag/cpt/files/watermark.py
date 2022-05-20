''' CPT files distribution watermarking DAG module '''
import datalabs.etl.dag.dag as dag
from   datalabs.etl.archive.transform import UnzipTransformerTask, ZipTransformerTask
from   datalabs.etl.control import DAGNotificationFactoryTask
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.pdf.transform import PDFSigningTransformerTask
from   datalabs.etl.sns.load import SNSMessageLoaderTask


class CoordinationDAG(dag.DAG):
    EXTRACT_USER_IDS: S3FileExtractorTask
    SCHEDULE_USER_DAGS: DAGNotificationFactoryTask
    NOTIFY_DAG_PROCESSOR: SNSMessageLoaderTask


class UserDAG(dag.DAG):
    EXTRACT_SIGNING_CREDENTIALS: S3FileExtractorTask
    EXTRACT_RELEASE_FILES: UnzipTransformerTask
    SIGN_PDFS: PDFSigningTransformerTask
    CREATE_DISTRIBUTION: ZipTransformerTask


# pylint: disable=pointless-statement

### Coordination DAG Edges ###

CoordinationDAG.EXTRACT_USER_IDS >> CoordinationDAG.SCHEDULE_USER_DAGS >> CoordinationDAG.NOTIFY_DAG_PROCESSOR


### User DAG Edges ###

UserDAG.EXTRACT_SIGNING_CREDENTIALS >> UserDAG.SIGN_PDFS
UserDAG.EXTRACT_RELEASE_FILES >> UserDAG.SIGN_PDFS

UserDAG.SIGN_PDFS >> UserDAG.CREATE_DISTRIBUTION
