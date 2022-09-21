''' DAG definition for CPT Files Process '''
from   datalabs.etl.cpt.extract import ReleaseFilesListExtractorTask
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.s3.extract import S3FileExtractorTask


class CPTCoreDAG(DAG):
    FIND_LINK_RELEASES: ReleaseFilesListExtractorTask
    EXTRACT_LINK_RELEASES: S3FileExtractorTask
    BUILD_CORE: 'datalabs.etl.cpt.build.CoreBuilderTask'


# pylint: disable=pointless-statement
CPTCoreDAG.FIND_LINK_RELEASES \
        >> CPTCoreDAG.EXTRACT_LINK_RELEASES \
        >> CPTCoreDAG.BUILD_CORE


class CPTLinkDAG(DAG):
    BUILD_LINK: 'datalabs.etl.cpt.build.LinkBuilderTask'


# pylint: disable=pointless-statement
CPTLinkDAG.BUILD_LINK
