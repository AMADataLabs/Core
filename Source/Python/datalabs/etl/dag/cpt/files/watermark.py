import datalabs.etl.dag.dag as dag
from   datalabs.etl.archive.transform import UnzipTransformerTask
from   datalabs.etl.s3.extract import S3FileLoaderTask, S3DirectoryListingExtractorTask
from   datalabs.etl.s3.load import S3FileReplicatorTask
from   datalabs.etl.pdf.transform import SignedPDFTransformerTask


class DAG(dag.DAG):
    EXTRACT_USER_IDS: S3FileLoaderTask
    EXTRACT_RELEASE_FILES: UnzipTransformerTask
    EXTRACT_RELEASE_FILE_LIST: S3DirectoryListingExtractorTask
    REPLICATE_TEXT_FILES: S3FileReplicatorTask
    SIGN_PDFS: SignedPDFTransformerTask


# pylint: disable=pointless-statement
DAG.EXTRACT_USER_IDS >> DAG.REPLICATE_TEXT_FILES

DAG.EXTRACT_RELEASE_FILES >> DAG.EXTRACT_RELEASE_FILE_LIST >> DAG.REPLICATE_TEXT_FILES

DAG.REPLICATE_TEXT_FILES >> DAG.SIGN_PDFS
