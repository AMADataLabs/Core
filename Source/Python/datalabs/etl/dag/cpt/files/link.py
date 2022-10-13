''' DAG definition for CPT Link Files Process '''
# from   datalabs.etl.cpt.files.link.extract import InputFilesListExtractorTask
from   datalabs.etl.dag.dag import DAG, register
# from   datalabs.etl.s3.extract import S3FileExtractorTask


@register(name="CPT_LINK")
class CPTLinkDAG(DAG):
    BUILD_LINK: 'datalabs.etl.cpt.build.LinkBuilderTask'


# pylint: disable=pointless-statement
CPTLinkDAG.BUILD_LINK
