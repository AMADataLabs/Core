from   datalabs.etl.dag.dag import DAG

from   datalabs.etl.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.cpt.organization import LicensedOrganizationTransformerTask
from   datalabs.etl.orm.load import ORMLoader


class LicensedOrganizationDAG(DAG):
    EXTRACT_LICENSED_ORGANIZATIONS: JDBCExtractorTask
    CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS: LicensedOrganizationTransformerTask
    LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS: ORMLoader


EXTRACT_LICENSED_ORGANIZATIONS >> CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS \
    >> LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS
