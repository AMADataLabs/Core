''' DAG definition for CPT Link Files Process '''
# pylint: disable=line-too-long
from   datalabs.etl.cpt.files.link.extract import InputFilesListExtractorTask
from   datalabs.etl.cpt.files.link.transform import TabDelimitedToFixedWidthDescriptorTransformerTask, UpperCaseDescriptorTransformerTask
from   datalabs.etl.dag.dag import DAG, register
from   datalabs.etl.s3.extract import S3FileExtractorTask


@register(name="CPT_LINK")
class CPTLinkDAG(DAG):
    FIND_INPUT_FILES: InputFilesListExtractorTask
    EXTRACT_INPUT_FILES: S3FileExtractorTask
    EXTRACT_EDITS: S3FileExtractorTask
    EXTRACT_RVUS: S3FileExtractorTask
    BUILD_LINK: 'datalabs.etl.cpt.build.LinkBuilderTask'
    GENERATE_FIXED_WIDTH_DESCRIPTOR_FILES: TabDelimitedToFixedWidthDescriptorTransformerTask
    GENERATE_LONGU_FILES: UpperCaseDescriptorTransformerTask


# pylint: disable=pointless-statement
CPTLinkDAG.FIND_INPUT_FILES >> CPTLinkDAG.EXTRACT_INPUT_FILES

CPTLinkDAG.EXTRACT_INPUT_FILES >> CPTLinkDAG.BUILD_LINK
CPTLinkDAG.EXTRACT_EDITS >> CPTLinkDAG.BUILD_LINK
CPTLinkDAG.EXTRACT_RVUS >> CPTLinkDAG.BUILD_LINK
CPTLinkDAG.BUILD_LINK >> CPTLinkDAG.GENERATE_FIXED_WIDTH_DESCRIPTOR_FILES
CPTLinkDAG.GENERATE_FIXED_WIDTH_DESCRIPTOR_FILES >> CPTLinkDAG.GENERATE_LONGU_FILES
