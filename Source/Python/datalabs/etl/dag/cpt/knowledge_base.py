''' DAG definition for KnowledgeBase-CPT API ETL '''
from   datalabs.etl.dag import dag
from   datalabs.etl.cpt.knowledge_base import load as Load
from   datalabs.etl.cpt.knowledge_base import transform as Transform



@dag.register(name="KNOWLEDGE_BASE_ETL")
class DAG(dag.DAG):
    EXTRACT_KNOWLEDGE_BASE_FILE: "datalabs.etl.s3.extract.S3FileExtractorTask"
    CREATE_KNOWLEDGE_BASE_DATA: "Transform.DataTransformerTask"
    LOAD_KNOWLEDGE_BASE_DATA: "Load.OpensearchLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_KNOWLEDGE_BASE_FILE >> DAG.CREATE_KNOWLEDGE_BASE_DATA  >> DAG.LOAD_KNOWLEDGE_BASE_DATA
