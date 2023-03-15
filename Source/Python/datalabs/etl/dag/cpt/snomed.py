''' DAG definition for CPT SNOMED Mapping '''
from   datalabs.etl.dag.dag import DAG, register


@register(name="SNOMED_MAPPING")
class SNOMEDMappingDAG(DAG):
    EXTRACT_SNOMED_FILE: "datalabs.etl.sftp.extract.SFTPFileExtractorTask"
    CREATE_SNOMED_MAPPINGS: "datalabs.etl.cpt.snomed.transform.SNOMEDMappingTransformerTask"
    LOAD_SNOMED_MAPPINGS: "datalabs.etl.dynamodb.load.DynamoDBLoaderTask"


# pylint: disable=pointless-statement
SNOMEDMappingDAG.EXTRACT_SNOMED_FILE >> SNOMEDMappingDAG.CREATE_SNOMED_MAPPINGS >> SNOMEDMappingDAG.LOAD_SNOMED_MAPPINGS
