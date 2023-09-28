''' DAG definition for KnowledgeBase-CPT API ETL '''
from   datalabs.etl.dag import dag
from   datalabs.etl.cpt.knowledge_base.load import OpensearchLoaderTask
from   datalabs.etl.cpt.knowledge_base.transform import DataTransformerTask



@dag.register(name="KNOWLEDGE_BASE_ETL")
class DAG(dag.DAG):
    EXTRACT_KNOWLEDGE_BASE_FILE: "datalabs.etl.s3.extract.S3FileExtractorTask"
    CREATE_KNOWLEDGE_BASE_DATA: "DataTransformerTask"
    LOAD_KNOWLEDGE_BASE_DATA: "OpensearchLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_KNOWLEDGE_BASE_FILE >> DAG.CREATE_KNOWLEDGE_BASE_DATA  >> DAG.LOAD_KNOWLEDGE_BASE_DATA
