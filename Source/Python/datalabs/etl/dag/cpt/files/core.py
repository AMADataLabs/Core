''' DAG definition for CPT Core Files Process '''
from   datalabs.etl.dag.dag import DAG, JavaTask


@register(name="CPT_CORE")
class CPTCoreDAG(DAG):
    FIND_INPUT_FILES: "datalabs.etl.cpt.files.core.extract.InputFilesListExtractorTask"
    EXTRACT_INPUT_FILES: "datalabs.etl.s3.extract.S3FileExtractorTask"
    BUILD_CORE: JavaTask("datalabs.etl.cpt.build.CoreBuilderTask")
    # BUILD_CONSUMER_AND_CLINICIAN_DESCRIPTORS: 'datalabs.etl.cpt.build.ConsumerClinicianBuilderTask'
    # LOAD_CONSUMER_AND_CLINICIAN_DESCRIPTORS: SMTPFileLoaderTask


# pylint: disable=pointless-statement
CPTCoreDAG.FIND_INPUT_FILES >> CPTCoreDAG.EXTRACT_INPUT_FILES >> CPTCoreDAG.BUILD_CORE
# >> CPTCoreDAG.BUILD_CONSUMER_AND_CLINICIAN_DESCRIPTORS >> CPTCoreDAG.LOAD_CONSUMER_AND_CLINICIAN_DESCRIPTORS
