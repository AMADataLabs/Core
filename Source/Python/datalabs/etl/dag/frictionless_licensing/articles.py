''' DAG definition for the Frictionless Licensing ETL. '''
from   datalabs.etl.dag.dag import DAG, Repeat
from   datalabs.etl.jdbc.extract import JDBCExtractorTask, JDBCParametricExtractorTask
from   datalabs.etl.orm.load import ORMLoaderTask


class ArticlesDAG(DAG):
    EXTRACT_PLATFORM_ARTICLES: JDBCExtractorTask
    CREATE_PLATFORM_ARTICLES: 'datalabs.etl.cpt.transform.PlatformTransformerTask'
    LOAD_PLATFORM_ARTICLES: ORMLoaderTask


# pylint: disable=pointless-statement
ArticlesDAG.EXTRACT_PLATFORM_ARTICLES >> ArticlesDAG.CREATE_PLATFORM_ARTICLES >> ArticlesDAG.LOAD_PLATFORM_ARTICLES
