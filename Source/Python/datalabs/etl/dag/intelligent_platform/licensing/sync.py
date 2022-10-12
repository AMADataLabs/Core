''' DAG definition for the Intelligent Platform Licensing ETL. '''
import datalabs.etl.dag.dag as dag

from   datalabs.etl.sql.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.intelligent_platform.licensing.transform import LicensedOrganizationsTransformerTask
from   datalabs.etl.intelligent_platform.licensing.transform import LicensedArticlesTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask


@dag.register(name="LICENSING")
class DAG(dag.DAG):
    EXTRACT_LICENSED_ORGANIZATIONS: JDBCExtractorTask
    CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS: LicensedOrganizationsTransformerTask
    LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS: ORMLoaderTask
    EXTRACT_ACTIVE_ARTICLES: JDBCExtractorTask
    CREATE_ACTIVE_ARTICLES: LicensedArticlesTransformerTask
    LOAD_ACTIVE_ARTICLES: ORMLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_LICENSED_ORGANIZATIONS \
    >> DAG.CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS \
    >> DAG.LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS

DAG.EXTRACT_ACTIVE_ARTICLES >> DAG.CREATE_ACTIVE_ARTICLES >> DAG.LOAD_ACTIVE_ARTICLES
