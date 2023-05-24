''' DAG definition for CPT Link Files Process '''
from   datalabs.etl.dag.dag import DAG, register, JavaTask


@register(name="CPT_LINK")
class CPTLinkDAG(DAG):
    BUILD_LINK: JavaTask("datalabs.etl.cpt.build.LinkBuilderTask")
    UNZIP_BUILDER_OUTPUT: "datalabs.etl.archive.transform.UnzipTransformerTask"
    GENERATE_FIXED_WIDTH_DESCRIPTOR_FILES: "datalabs.etl.cpt.files.link.transform.TabDelimitedToFixedWidthDescriptorTransformerTask"
    GENERATE_UPPER_CASE_DESCRIPTOR_FILES: "datalabs.etl.cpt.files.link.transform.UpperCaseDescriptorTransformerTask"
    CREATE_STANDARD_BUNDLE: "datalabs.etl.archive.transform.ZipTransformerTask"
    CREATE_LINK_BUNDLE: "datalabs.etl.archive.transform.ZipTransformerTask"


# pylint: disable=pointless-statement
CPTLinkDAG.BUILD_LINK \
    >> CPTLinkDAG.UNZIP_BUILDER_OUTPUT \
    >> CPTLinkDAG.GENERATE_FIXED_WIDTH_DESCRIPTOR_FILES \
    >> CPTLinkDAG.GENERATE_UPPER_CASE_DESCRIPTOR_FILES

CPTLinkDAG.UNZIP_BUILDER_OUTPUT >> CPTLinkDAG.CREATE_STANDARD_BUNDLE
CPTLinkDAG.GENERATE_UPPER_CASE_DESCRIPTOR_FILES >> CPTLinkDAG.CREATE_STANDARD_BUNDLE

CPTLinkDAG.UNZIP_BUILDER_OUTPUT >> CPTLinkDAG.CREATE_LINK_BUNDLE
CPTLinkDAG.GENERATE_UPPER_CASE_DESCRIPTOR_FILES >> CPTLinkDAG.CREATE_LINK_BUNDLE
