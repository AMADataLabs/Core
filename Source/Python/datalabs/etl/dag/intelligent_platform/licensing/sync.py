''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag import dag
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.intelligent_platform.licensing.sync.transform import \
    LicensedOrganizationsTransformerTask, \
    LicensedArticlesTransformerTask
    # ContractStatusTransformerTask, \
from   datalabs.etl.orm.load import ORMLoaderTask


@dag.register(name="LICENSING")
class DAG(dag.DAG):
    CREATE_ACTIVE_ARTICLES: LicensedArticlesTransformerTask
    # CREATE_CONTRACT_STATUS_TABLE: ContractStatusTransformerTask
    CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS: LicensedOrganizationsTransformerTask
    EXTRACT_ACTIVE_ARTICLES: SQLAlchemyExtractorTask
    # EXTRACT_API_CONTRACTS: SQLAlchemyExtractorTask
    # EXTRACT_CONTRACT_APPROVED_CONTENT: SQLAlchemyExtractorTask
    # EXTRACT_CONTRACT_DENIED_CONTENT: SQLAlchemyExtractorTask
    EXTRACT_LICENSED_ORGANIZATIONS: SQLAlchemyExtractorTask
    LOAD_ACTIVE_ARTICLES: ORMLoaderTask
    LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS: ORMLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_LICENSED_ORGANIZATIONS \
    >> DAG.CREATE_FRICTIONLESS_LICENSING_ORGANIZATIONS \
    >> DAG.LOAD_FRICTIONLESS_LICENSING_ORGANIZATIONS

DAG.EXTRACT_ACTIVE_ARTICLES >> DAG.CREATE_ACTIVE_ARTICLES >> DAG.LOAD_ACTIVE_ARTICLES


# DAG.EXTRACT_API_CONTRACTS >> DAG.CREATE_CONTRACT_STATUS_TABLE
# DAG.EXTRACT_CONTRACT_APPROVED_CONTENT >> DAG.CREATE_CONTRACT_STATUS_TABLE
# DAG.EXTRACT_CONTRACT_DENIED_CONTENT >> DAG.CREATE_CONTRACT_STATUS_TABLE
