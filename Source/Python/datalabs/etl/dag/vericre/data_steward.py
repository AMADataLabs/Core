''' VeriCre Data Steward Download DAG definition. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.smtp.load import SMTPFileLoaderTask
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask


@dag.register(name='VERICRE_DATA_STEWARD')
class DAG(dag.DAG):
    EXTRACT_NEW_USER_PATHS_TODAY: SQLAlchemyExtractorTask
    GENERATE_USER_UPLOADS_PATHS: 'UserDirectoryTransformerTask'
    EXTRACT_USER_UPLOADS: S3FileExtractorTask
    ZIP_USER_UPLOADS: 'ZIPFileLoaderTask'
    SEND_USER_UPLOADS: SMTPFileLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_NEW_USER_PATHS_TODAY \
        >> DAG.GENERATE_USER_UPLOADS_PATHS \
        >> DAG.EXTRACT_USER_UPLOADS \
        >> DAG.ZIP_USER_UPLOADS \
        >> DAG.SEND_USER_UPLOADS
