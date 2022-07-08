''' DAG definition for the Frictionless Licensing ETL. '''
from   datalabs.etl.dag.dag import DAG, Repeat
from   datalabs.etl.jdbc.extract import JDBCExtractorTask, JDBCParametricExtractorTask
from   datalabs.etl.orm.load import ORMLoaderTask


class ArticlesDAG(DAG):
    EXTRACT_ACTIVE_ARTICLES: JDBCExtractorTask
    CREATE_ACTIVE_ARTICLES: 'datalabs.etl.cpt.organization.transform.PlatformTransformerTask'
    LOAD_ACTIVE_ARTICLES: ORMLoaderTask


# pylint: disable=pointless-statement
ArticlesDAG.EXTRACT_ACTIVE_ARTICLES >> ArticlesDAG.CREATE_ACTIVE_ARTICLES >> ArticlesDAG.LOAD_ACTIVE_ARTICLES
