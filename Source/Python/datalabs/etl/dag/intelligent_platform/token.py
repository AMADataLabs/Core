''' DAG definition for the Email Report ETL. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.intelligent_platform.token import ExpiredTokenPurgeTask


@dag.register(name="PLATFORM_USER_TOKENS")
class DAG(dag.DAG):
    DELETE_EXPIRED_TOKENS: ExpiredTokenPurgeTask


# pylint: disable=pointless-statement
