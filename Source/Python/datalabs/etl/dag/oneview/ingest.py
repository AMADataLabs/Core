''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.oneview.melissa.transform import MelissaTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask

class OneViewDAG(DAG):
    EXTRACT_MELISSA: S3FileExtractorTask
    CREATE_MELISSA_TABLES: MelissaTransformerTask
    LOAD_MELISSA_TABLES_INTO_DATABASE: ORMLoaderTask


# pylint: disable=pointless-statement
OneViewDAG.EXTRACT_MELISSA >> OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_MELISSA_TABLES_INTO_DATABASE
