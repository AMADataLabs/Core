''' DAG definition for the Email Report ETL. '''
from   datalabs.etl.dag import dag
from   datalabs import feature
from   datalabs.etl.intelligent_platform.developer.email.load import EmailReportSMTPLoaderTask
from   datalabs.etl.sql.sqlalchemy.extract import SQLAlchemyExtractorTask
from   datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
from   datalabs.etl.http.extract import HTTPFileListExtractorTask
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
if feature.enabled("DL_3436"):
    from    datalabs.etl.vericre.profile.transform import AMAProfilesTransformerTask
    from    datalabs.etl.vericre.profile.transform import VeriCreProfileSynchronizerTask


from   datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
from   datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask
from   datalabs.etl.qldb.load import QLDBLoaderTask

@dag.register(name="DEVELOPER_EMAILS")

class DAG(dag.DAG):
    EXTRACT_AMA_PHYSICIAN_PROFILES: SFTPFileExtractorTask
    CREATE_AMA_PROFILE_TABLE: AMAProfilesTransformerTask
    LOAD_AMA_PROFILES_TO_LEDGER: QLDBLoaderTask
    SYNC_PROFILES_TO_DATABASE: VeriCreProfileSynchronizerTask

    CREATE_CAQH_STATUS_URLS: CAQHStatusURLListTransformerTask
    EXTRACT_CAQH_PHYSICIAN_STATUSES: HTTPFileListExtractorTask
    CREATE_CAQH_PROFILE_URLS: CAQHProfileURLListTranformerTask

    EXTRACT_CAQH_PHYSICIAN_PROFILES: HTTPFileListExtractorTask
    CREATE_CAQH_PROFILE_TABLE: CAQHProfileURLListTranformerTask
    LOAD_CAQH_PROFILES_TO_LEDGER: QLDBLoaderTask


# pylint: disable=pointless-statement
DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> \
    DAG.CREATE_AMA_PROFILE_TABLE
DAG.LOAD_AMA_PROFILES_TO_LEDGER >> \
    DAG.SYNC_PROFILES_TO_DATABASE
DAG.CREATE_CAQH_STATUS_URLS >> \
    DAG.EXTRACT_CAQH_PHYSICIAN_STATUSES >> \
    DAG.CREATE_CAQH_PROFILE_URLS >> \
    DAG.EXTRACT_CAQH_PHYSICIAN_PROFILES >> \
    DAG.CREATE_CAQH_PROFILE_TABLE >> \
    DAG.LOAD_CAQH_PROFILES_TO_LEDGER

