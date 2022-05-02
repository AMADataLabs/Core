''' CPT files distribution watermarking DAG module '''
import datalabs.etl.dag.dag as dag
from   datalabs.etl.archive.transform import UnzipTransformerTask, ZipTransformerTask
from   datalabs.etl.s3.extract import S3FileExtractorTask, S3DirectoryListingExtractorTask
from   datalabs.etl.s3.load import S3FileReplicatorTask
from   datalabs.etl.pdf.transform import SignedPDFTransformerTask


class DAG(dag.DAG):
    EXTRACT_USER_IDS: S3FileExtractorTask
    EXTRACT_RELEASE_FILES: UnzipTransformerTask
    EXTRACT_RELEASE_FILE_LIST: S3DirectoryListingExtractorTask
    REPLICATE_TEXT_FILES: S3FileReplicatorTask
    SIGN_PDFS: SignedPDFTransformerTask
    CREATE_WATERMARKED_DISTRIBUTIONS: ZipTransformerTask



# pylint: disable=pointless-statement
DAG.EXTRACT_USER_IDS >> DAG.REPLICATE_TEXT_FILES

DAG.EXTRACT_RELEASE_FILES >> DAG.EXTRACT_RELEASE_FILE_LIST >> DAG.REPLICATE_TEXT_FILES

DAG.REPLICATE_TEXT_FILES >> DAG.SIGN_PDFS >> DAG.CREATE_WATERMARKED_DISTRIBUTIONS
