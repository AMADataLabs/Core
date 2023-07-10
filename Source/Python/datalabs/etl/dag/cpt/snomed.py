''' DAG definition for SNOMED-CPT API ETL '''
from   datalabs.etl.dag import dag, Repeat


@dag.register(name="SNOMED_CPT_ETL")
class DAG(dag.DAG):
    EXTRACT_SNOMED_FILE: "datalabs.etl.s3.extract.S3FileExtractorTask"
    CREATE_SNOMED_MAPPINGS: "datalabs.etl.cpt.snomed.transform.SNOMEDMappingTransformerTask"
    SPLIT_MAPPINGS: "datalabs.etl.manipulate.transform.SplitTransformerTask"
    LOAD_SNOMED_MAPPINGS: Repeat("datalabs.etl.cpt.snomed.load.DynamoDBLoaderTask", 4)


# pylint: disable=pointless-statement
DAG.EXTRACT_SNOMED_FILE >> DAG.CREATE_SNOMED_MAPPINGS >> DAG.SPLIT_MAPPINGS >> DAG.first('LOAD_SNOMED_MAPPINGS')
DAG.sequence('LOAD_SNOMED_MAPPINGS')
