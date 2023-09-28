''' DAG definition for KnowledgeBase-CPT API ETL '''
from   datalabs.etl.dag import dag
from   datalabs.etl.cpt.knowledge_base import transform
from   datalabs.etl.cpt.knowledge_base import load



@dag.register(name="KNOWLEDGE_BASE_ETL")
class DAG(dag.DAG):
    EXTRACT_KNOWLEDGE_BASE_FILE: "datalabs.etl.s3.extract.S3FileExtractorTask"
    CREATE_KNOWLEDGE_BASE_DATA: "transform.DataTransformerTask"
    LOAD_KNOWLEDGE_BASE_DATA: "load.OpensearchLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_KNOWLEDGE_BASE_FILE >> DAG.CREATE_KNOWLEDGE_BASE_DATA  >> DAG.LOAD_KNOWLEDGE_BASE_DATA
