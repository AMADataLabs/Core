''' DAG definition for SNOMED-CPT API ETL '''
from   datalabs.etl.dag import dag


@dag.register(name="SNOMED_CPT")
class DAG(dag.DAG):
    EXTRACT_SNOMED_FILE: "datalabs.etl.s3.extract.S3FileExtractorTask"
    CREATE_SNOMED_MAPPINGS: "datalabs.etl.cpt.snomed.transform.SNOMEDMappingTransformerTask"
    # LOAD_SNOMED_MAPPINGS: "datalabs.etl.dynamodb.load.DynamoDBLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_SNOMED_FILE >> DAG.CREATE_SNOMED_MAPPINGS # >> DAG.LOAD_SNOMED_MAPPINGS
