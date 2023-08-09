''' DAG definition for PROFILES '''
from datalabs import feature
from datalabs.etl.dag import dag
from datalabs.etl.http.extract import HTTPFileListExtractorTask
from datalabs.etl.manipulate.transform import DateFormatTransformerTask
from datalabs.etl.qldb.load import QLDBLoaderTask
from datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask
from datalabs.etl.vericre.profile.transform import JSONTransformerTask
from datalabs.etl.sftp.extract import SFTPFileExtractorTask


# pylint: disable=no-name-in-module
from datalabs.etl.vericre.profile.transform import AMAProfilesTransformerTask

if feature.enabled("DL_3462"):
    from datalabs.etl.vericre.profile.transform import CAQHProfileTransformerTask

if feature.enabled("DL_3436"):
    from datalabs.etl.vericre.profile.transform import VeriCreProfileSynchronizerTask


@dag.register(name="VERICRE_PROFILES_ETL")
class DAG(dag.DAG):
    EXTRACT_AMA_PHYSICIAN_PROFILES: SFTPFileExtractorTask
    STANDARDIZE_DATES: DateFormatTransformerTask
    CREATE_AMA_PROFILE_TABLE: AMAProfilesTransformerTask
    CONVERT_AMA_MASTERFILE_TO_JSON: JSONTransformerTask
    LOAD_AMA_MASTERFILE_TABLE: dag.Repeat(QLDBLoaderTask, 20)

    if feature.enabled("CAQH_PROFILES"):
        CREATE_CAQH_STATUS_URLS: CAQHStatusURLListTransformerTask
        EXTRACT_CAQH_PROFILE_STATUSES: HTTPFileListExtractorTask
        CREATE_CAQH_PROFILE_URLS: CAQHProfileURLListTranformerTask
        EXTRACT_CAQH_PHYSICIAN_PROFILES: HTTPFileListExtractorTask
        if feature.enabled("DL_3462"):
            CREATE_CAQH_PROFILE_TABLE: CAQHProfileTransformerTask
        LOAD_CAQH_PROFILES_TO_LEDGER: QLDBLoaderTask

    if feature.enabled("DL_3436"):
        SYNC_PROFILES_TO_DATABASE: VeriCreProfileSynchronizerTask


# pylint: disable=expression-not-assigned, pointless-statement
if feature.enabled("DL_3436"):
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES \
        >> DAG.STANDARDIZE_DATES \
        >> DAG.CREATE_AMA_PROFILE_TABLE \
        >> DAG.CONVERT_AMA_MASTERFILE_TO_JSON \
        >> DAG.first('LOAD_AMA_MASTERFILE_TABLE')

    DAG.sequence('LOAD_AMA_MASTERFILE_TABLE')

    DAG.last('LOAD_AMA_MASTERFILE_TABLE') >> DAG.SYNC_PROFILES_TO_DATABASE
else:
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES \
        >> DAG.STANDARDIZE_DATES \
        >> DAG.CREATE_AMA_PROFILE_TABLE \
        >> DAG.CONVERT_AMA_MASTERFILE_TO_JSON \
        >> DAG.first('LOAD_AMA_MASTERFILE_TABLE')

    DAG.sequence('LOAD_AMA_MASTERFILE_TABLE')

if feature.enabled("CAQH_PROFILES"):
    DAG.CREATE_AMA_PROFILE_TABLE \
        >> DAG.CREATE_CAQH_STATUS_URLS \
        >> DAG.EXTRACT_CAQH_PROFILE_STATUSES \
        >> DAG.CREATE_CAQH_PROFILE_URLS \
        >> DAG.EXTRACT_CAQH_PHYSICIAN_PROFILES \
        >> DAG.LOAD_CAQH_PROFILES_TO_LEDGER \
        >> DAG.SYNC_PROFILES_TO_DATABASE
