''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag.dag import DAG

from   datalabs.etl.sql.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.intelligent_platform.licensing.transform import LicensedOrganizationsTransformerTask
from   datalabs.etl.intelligent_platform.licensing.transform import LicensedArticlesTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask


class LicensingDAG(DAG):
    EXTRACT_LICENSED_ORGANIZATIONS: JDBCExtractorTask
    CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS: LicensedOrganizationsTransformerTask
    LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS: ORMLoaderTask
    EXTRACT_ACTIVE_ARTICLES: JDBCExtractorTask
    CREATE_ACTIVE_ARTICLES: LicensedArticlesTransformerTask
    LOAD_ACTIVE_ARTICLES: ORMLoaderTask


# pylint: disable=pointless-statement
LicensingDAG.EXTRACT_LICENSED_ORGANIZATIONS \
    >> LicensingDAG.CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS \
    >> LicensingDAG.LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS

LicensingDAG.EXTRACT_ACTIVE_ARTICLES >> LicensingDAG.CREATE_ACTIVE_ARTICLES >> LicensingDAG.LOAD_ACTIVE_ARTICLES
