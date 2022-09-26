''' DAG definition for CPT Core Files Process '''
from   datalabs.etl.cpt.files.core.extract import InputFilesListExtractorTask
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.s3.extract import S3FileExtractorTask


class CPTCoreDAG(DAG):
    FIND_INPUT_RELEASES: InputFilesListExtractorTask
    EXTRACT_INPUT_FILES: S3FileExtractorTask
    BUILD_CORE: 'datalabs.etl.cpt.build.CoreBuilderTask'


# pylint: disable=pointless-statement
CPTCoreDAG.FIND_INPUT_RELEASES \
        >> CPTCoreDAG.EXTRACT_INPUT_FILES \
        >> CPTCoreDAG.BUILD_CORE
