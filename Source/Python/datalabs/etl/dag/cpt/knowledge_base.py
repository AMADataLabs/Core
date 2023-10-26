''' DAG definition for KnowledgeBase-CPT API ETL '''
from   datalabs.etl.dag import dag

@dag.register(name="CPT_KNOWLEDGE_BASE_ETL")
class DAG(dag.DAG):
    EXTRACT_KNOWLEDGE_BASE_FILE: "datalabs.etl.sftp.extract.SFTPFileExtractorTask"
    CREATE_KNOWLEDGE_BASE_DATA: "datalabs.etl.cpt.knowledge_base.transform.KnowledgeBaseTransformerTask"
    LOAD_KNOWLEDGE_BASE_DATA: "datalabs.etl.cpt.knowledge_base.load.OpenSearchLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_KNOWLEDGE_BASE_FILE >> DAG.CREATE_KNOWLEDGE_BASE_DATA  >> DAG.LOAD_KNOWLEDGE_BASE_DATA
