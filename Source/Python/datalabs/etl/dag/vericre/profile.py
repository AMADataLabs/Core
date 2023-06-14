from datalabs import feature
from datalabs.etl.dag import dag
from datalabs.etl.http.extract import HTTPFileListExtractorTask
from datalabs.etl.qldb.load import QLDBLoaderTask
from datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask
from datalabs.etl.sftp.extract import SFTPFileExtractorTask
if feature.enabled("DL_3436"):
    from datalabs.etl.vericre.profile.transform import AMAProfilesTransformerTask
    from datalabs.etl.vericre.profile.transform import VeriCreProfileSynchronizerTask


@dag.register(name="PROFILES")
class DAG(dag.DAG):
    EXTRACT_AMA_PHYSICIAN_PROFILES: SFTPFileExtractorTask
    if feature.enabled("DL_3436"):
        CREATE_AMA_PROFILE_TABLE: AMAProfilesTransformerTask
    LOAD_AMA_PROFILES_TO_LEDGER: QLDBLoaderTask
    if feature.enabled("DL_3436"):
        SYNC_PROFILES_TO_DATABASE: VeriCreProfileSynchronizerTask

    CREATE_CAQH_STATUS_URLS: CAQHStatusURLListTransformerTask
    EXTRACT_CAQH_PHYSICIAN_STATUSES: HTTPFileListExtractorTask
    CREATE_CAQH_PROFILE_URLS: CAQHProfileURLListTranformerTask

    EXTRACT_CAQH_PHYSICIAN_PROFILES: HTTPFileListExtractorTask
    CREATE_CAQH_PROFILE_TABLE: CAQHProfileURLListTranformerTask
    LOAD_CAQH_PROFILES_TO_LEDGER: QLDBLoaderTask


DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> (
    DAG.CREATE_AMA_PROFILE_TABLE >> DAG.LOAD_AMA_PROFILES_TO_LEDGER if feature.enabled("DL_3436") else DAG.LOAD_AMA_PROFILES_TO_LEDGER
) >> (
    DAG.SYNC_PROFILES_TO_DATABASE >> DAG.CREATE_CAQH_STATUS_URLS if feature.enabled("DL_3436") else DAG.CREATE_CAQH_STATUS_URLS
) >> DAG.EXTRACT_CAQH_PHYSICIAN_STATUSES >> DAG.CREATE_CAQH_PROFILE_URLS >> DAG.EXTRACT_CAQH_PHYSICIAN_PROFILES >> DAG.CREATE_CAQH_PROFILE_TABLE >> DAG.LOAD_CAQH_PROFILES_TO_LEDGER

