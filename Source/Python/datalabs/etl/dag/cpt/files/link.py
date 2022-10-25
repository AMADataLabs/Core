''' DAG definition for CPT Link Files Process '''
from   datalabs.etl.cpt.files.link.extract import InputFilesListExtractorTask
from   datalabs.etl.dag.dag import DAG, register
from   datalabs.etl.s3.extract import S3FileExtractorTask


@register(name="CPT_LINK")
class CPTLinkDAG(DAG):
    FIND_INPUT_FILES: InputFilesListExtractorTask
    EXTRACT_INPUT_FILES: S3FileExtractorTask
    EXTRACT_EDITS: S3FileExtractorTask
    EXTRACT_RVUS: S3FileExtractorTask
    BUILD_LINK: 'datalabs.etl.cpt.build.LinkBuilderTask'


# pylint: disable=pointless-statement
CPTLinkDAG.FIND_INPUT_FILES \
    >> CPTLinkDAG.EXTRACT_INPUT_FILES \
    >> CPTLinkDAG.EXTRACT_EDITS \
    >> CPTLinkDAG.EXTRACT_RVUS \
    >> CPTLinkDAG.BUILD_LINK
