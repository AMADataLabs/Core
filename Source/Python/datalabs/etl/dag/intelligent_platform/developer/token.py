''' DAG definition for the Email Report ETL. '''
import datalabs.etl.dag.dag as dag
from   datalabs.etl.cpt.developer.load import EmailReportSMTPLoaderTask


@dag.register(name="DEVELOPER_TOKENS")
class DAG(dag.DAG):
    DELETE_EXPIRED_TOKENS: "datalabs.etl.intelligent_platform.developer.token.ExpiredTokenPurgeTask"


# pylint: disable=pointless-statement
