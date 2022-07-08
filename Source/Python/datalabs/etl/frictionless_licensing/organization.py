''' DAG definition for the Frictionless Licensing organizations ETL. '''
from   datalabs.etl.dag.dag import DAG

from   datalabs.etl.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.frictionless_licensing.transform import LicensedOrganizationsTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask


class LicensedOrganizationDAG(DAG):
    EXTRACT_LICENSED_ORGANIZATIONS: JDBCExtractorTask
    CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS: LicensedOrganizationsTransformerTask
    LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS: ORMLoaderTask


# pylint: disable=pointless-statement
LicensedOrganizationDAG.EXTRACT_LICENSED_ORGANIZATIONS \
    >> LicensedOrganizationDAG.CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS \
    >> LicensedOrganizationDAG.LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS
