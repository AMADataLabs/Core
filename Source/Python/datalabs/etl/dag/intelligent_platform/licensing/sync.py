''' DAG definition for the Intelligent Platform Licensing ETL. '''
from   datalabs.etl.dag import dag


@dag.register(name="LICENSING_SYNC")
class DAG(dag.DAG):
    CREATE_ACTIVE_ARTICLES_TABLE: "datalabs.etl.intelligent_platform.licensing.sync.transform.ArticlesTransformerTask"
    # CREATE_CONTRACT_STATUS_TABLE: "datalabs.etl.intelligent_platform.licensing.sync.transform.ContractStatusTransformerTask"
    CREATE_ORGANIZATIONS_TABLE: "datalabs.etl.intelligent_platform.licensing.sync.transform.LicensedOrganizationsTransformerTask"
    EXTRACT_ACTIVE_ARTICLES: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    EXTRACT_ACTIVE_CONTRACT_ORGANIZATIONS: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    EXTRACT_CONTRACT_RIGHTS_ORGANIZATIONS: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    # EXTRACT_API_CONTRACTS: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    # EXTRACT_CONTRACT_APPROVED_CONTENT: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    # EXTRACT_CONTRACT_DENIED_CONTENT: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    EXTRACT_LICENSED_ORGANIZATIONS: "datalabs.etl.sql.sqlalchemy.extract.SQLAlchemyExtractorTask"
    LOAD_ACTIVE_ARTICLES_TABLE: "datalabs.etl.orm.load.ORMLoaderTask"
    LOAD_ORGANIZATIONS_TABLE: "datalabs.etl.orm.load.ORMLoaderTask"


# pylint: disable=pointless-statement
DAG.EXTRACT_ACTIVE_ARTICLES >> DAG.CREATE_ACTIVE_ARTICLES_TABLE >> DAG.LOAD_ACTIVE_ARTICLES_TABLE


DAG.EXTRACT_LICENSED_ORGANIZATIONS >> DAG.CREATE_ORGANIZATIONS_TABLE
DAG.EXTRACT_ACTIVE_CONTRACT_ORGANIZATIONS >> DAG.CREATE_ORGANIZATIONS_TABLE
DAG.EXTRACT_CONTRACT_RIGHTS_ORGANIZATIONS >> DAG.CREATE_ORGANIZATIONS_TABLE
DAG.CREATE_ORGANIZATIONS_TABLE >> DAG.LOAD_ORGANIZATIONS_TABLE


# DAG.EXTRACT_API_CONTRACTS >> DAG.CREATE_CONTRACT_STATUS_TABLE
# DAG.EXTRACT_CONTRACT_APPROVED_CONTENT >> DAG.CREATE_CONTRACT_STATUS_TABLE
# DAG.EXTRACT_CONTRACT_DENIED_CONTENT >> DAG.CREATE_CONTRACT_STATUS_TABLE
