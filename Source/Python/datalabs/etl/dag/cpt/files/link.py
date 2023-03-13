''' DAG definition for CPT Link Files Process '''
from   datalabs.etl.dag.dag import DAG, register, JavaTask


@register(name="CPT_LINK")
class CPTLinkDAG(DAG):
    FIND_INPUT_FILES: "datalabs.etl.cpt.files.core.extract.InputFilesListExtractorTask"
    EXTRACT_STATIC_INPUT_FILES: "datalabs.etl.s3.extract.S3FileExtractorTask"
    EXTRACT_STAGED_INPUT_FILES: "datalabs.etl.s3.extract.S3FileExtractorTask"
    SCRAPE_HCPCS_REPORTS: "datalabs.etl.cpt.hcpcs.extract.HCPCSQuarterlyUpdateReportURLExtractorTask"
    EXTRACT_HCPCS_REPORT: "datalabs.etl.http.extract.HTTPFileListExtractorTask"
    UNZIP_HCPCS_REPORTS: "datalabs.etl.archive.transform.UnzipTransformerTask"
    BUILD_LINK: JavaTask("datalabs.etl.cpt.build.LinkBuilderTask")


# pylint: disable=pointless-statement
CPTLinkDAG.FIND_INPUT_FILES >> CPTLinkDAG.BUILD_LINK
CPTLinkDAG.EXTRACT_STATIC_INPUT_FILES >> CPTLinkDAG.BUILD_LINK
CPTLinkDAG.EXTRACT_STAGED_INPUT_FILES >> CPTLinkDAG.BUILD_LINK
CPTLinkDAG.SCRAPE_HCPCS_REPORTS >> CPTLinkDAG.EXTRACT_HCPCS_REPORT >> CPTLinkDAG.UNZIP_HCPCS_REPORTS \
    >> CPTLinkDAG.BUILD_LINK
