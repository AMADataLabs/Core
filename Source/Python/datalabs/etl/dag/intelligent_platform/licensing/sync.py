''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag import dag, PythonTask
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.intelligent_platform.licensing.sync.transform import \
    LicensedOrganizationsTransformerTask, \
    ArticlesTransformerTask
    # ContractStatusTransformerTask, \
from   datalabs.etl.orm.load import ORMLoaderTask


@dag.register(name="LICENSING_SYNC")
class DAG(dag.DAG):
    CREATE_ACTIVE_ARTICLES_TABLE: ArticlesTransformerTask
    # CREATE_CONTRACT_STATUS_TABLE: ContractStatusTransformerTask
    CREATE_ORGANIZATIONS_TABLE: LicensedOrganizationsTransformerTask
    EXTRACT_ACTIVE_ARTICLES: SQLAlchemyExtractorTask
    EXTRACT_ACTIVE_CONTRACT_ORGANIZATIONS: SQLAlchemyExtractorTask
    EXTRACT_CONTRACT_RIGHTS_ORGANIZATIONS: SQLAlchemyExtractorTask
    # EXTRACT_API_CONTRACTS: SQLAlchemyExtractorTask
    # EXTRACT_CONTRACT_APPROVED_CONTENT: SQLAlchemyExtractorTask
    # EXTRACT_CONTRACT_DENIED_CONTENT: SQLAlchemyExtractorTask
    EXTRACT_LICENSED_ORGANIZATIONS: SQLAlchemyExtractorTask
    LOAD_ACTIVE_ARTICLES_TABLE: ORMLoaderTask
    LOAD_ORGANIZATIONS_TABLE: ORMLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_ACTIVE_ARTICLES >> DAG.CREATE_ACTIVE_ARTICLES_TABLE >> DAG.LOAD_ACTIVE_ARTICLES_TABLE


DAG.EXTRACT_LICENSED_ORGANIZATIONS >> DAG.CREATE_ORGANIZATIONS_TABLE
DAG.EXTRACT_ACTIVE_CONTRACT_ORGANIZATIONS >> DAG.CREATE_ORGANIZATIONS_TABLE
DAG.EXTRACT_CONTRACT_RIGHTS_ORGANIZATIONS >> DAG.CREATE_ORGANIZATIONS_TABLE
DAG.CREATE_ORGANIZATIONS_TABLE >> DAG.LOAD_ORGANIZATIONS_TABLE


# DAG.EXTRACT_API_CONTRACTS >> DAG.CREATE_CONTRACT_STATUS_TABLE
# DAG.EXTRACT_CONTRACT_APPROVED_CONTENT >> DAG.CREATE_CONTRACT_STATUS_TABLE
# DAG.EXTRACT_CONTRACT_DENIED_CONTENT >> DAG.CREATE_CONTRACT_STATUS_TABLE
