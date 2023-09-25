''' DAG definition for PROFILES '''
from datalabs import feature
from datalabs.etl.dag import dag
from datalabs.etl.http.extract import HTTPFileListExtractorTask
from datalabs.etl.manipulate.transform import DateFormatTransformerTask
from datalabs.etl.qldb.load import QLDBLoaderTask
from datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask
from datalabs.etl.vericre.profile.transform import JSONTransformerTask
from datalabs.etl.vericre.profile.transform import AMAProfileTransformerTask
from datalabs.etl.vericre.profile.transform import CAQHProfileTransformerTask
from datalabs.etl.vericre.profile.transform import DemographicsTransformerTask
from datalabs.etl.vericre.profile.transform import DeaTransformerTask
from datalabs.etl.vericre.profile.transform import NPITransformerTask
from datalabs.etl.vericre.profile.transform import MedicalSchoolsTransformerTask
from datalabs.etl.vericre.profile.transform import ABMSTransformerTask
from datalabs.etl.vericre.profile.transform import MedicalTrainingTransformerTask
from datalabs.etl.vericre.profile.transform import LicensesTransformerTask
from datalabs.etl.vericre.profile.transform import SanctionsTransformerTask
from datalabs.etl.vericre.profile.load import VeriCreProfileSynchronizerTask
from datalabs.etl.sftp.extract import SFTPFileExtractorTask


@dag.register(name="VERICRE_PROFILES_ETL")
class DAG(dag.DAG):
    EXTRACT_AMA_PHYSICIAN_PROFILES: SFTPFileExtractorTask
    STANDARDIZE_DATES_ABMS: DateFormatTransformerTask
    STANDARDIZE_DATES_DEA: DateFormatTransformerTask
    STANDARDIZE_DATES_DEMOG: DateFormatTransformerTask
    STANDARDIZE_DATES_LICENSE: DateFormatTransformerTask
    STANDARDIZE_DATES_MED_SCH: DateFormatTransformerTask
    STANDARDIZE_DATES_MED_TRAIN: DateFormatTransformerTask
    STANDARDIZE_DATES_NPI: DateFormatTransformerTask
    STANDARDIZE_DATES_SANCTIONS: DateFormatTransformerTask

    CREATE_AGGREGATED_DEMOG: DemographicsTransformerTask
    CREATE_AGGREGATED_DEA: DeaTransformerTask
    CREATE_AGGREGATED_NPI: NPITransformerTask
    CREATE_AGGREGATED_MED_SCH: MedicalSchoolsTransformerTask
    CREATE_AGGREGATED_ABMS: ABMSTransformerTask
    CREATE_AGGREGATED_MED_TRAIN: MedicalTrainingTransformerTask
    CREATE_AGGREGATED_LICENSES: LicensesTransformerTask
    CREATE_AGGREGATED_SANCTIONS: SanctionsTransformerTask
    CREATE_AMA_PROFILE_TABLE: AMAProfileTransformerTask
    CONVERT_AMA_MASTERFILE_TO_JSON: JSONTransformerTask
    LOAD_AMA_MASTERFILE_TABLE: dag.Repeat(QLDBLoaderTask, 20)

    if feature.enabled("CAQH_PROFILES"):
        CREATE_CAQH_STATUS_URLS: CAQHStatusURLListTransformerTask
        EXTRACT_CAQH_PROFILE_STATUSES: HTTPFileListExtractorTask
        CREATE_CAQH_PROFILE_URLS: CAQHProfileURLListTranformerTask
        EXTRACT_CAQH_PHYSICIAN_PROFILES: HTTPFileListExtractorTask
        CREATE_CAQH_PROFILE_TABLE: CAQHProfileTransformerTask
        LOAD_CAQH_PROFILES_TO_LEDGER: QLDBLoaderTask

    if feature.enabled("SYNC_PROFILES"):
        SYNC_PROFILES_TO_DATABASE: VeriCreProfileSynchronizerTask


# pylint: disable=expression-not-assigned, pointless-statement
if feature.enabled("SYNC_PROFILES"):
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_ABMS >> DAG.CREATE_AGGREGATED_ABMS >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_DEA >> DAG.CREATE_AGGREGATED_DEA >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_DEMOG >> DAG.CREATE_AGGREGATED_DEMOG >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_LICENSE >> DAG.CREATE_AGGREGATED_LICENSES >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_MED_SCH >> DAG.CREATE_AGGREGATED_MED_SCH >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_MED_TRAIN >> DAG.CREATE_AGGREGATED_MED_TRAIN >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_NPI >> DAG.CREATE_AGGREGATED_NPI >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_SANCTIONS >> DAG.CREATE_AGGREGATED_SANCTIONS >> DAG.CREATE_AMA_PROFILE_TABLE

    DAG.CREATE_AMA_PROFILE_TABLE \
        >> DAG.CONVERT_AMA_MASTERFILE_TO_JSON \
        >> DAG.first('LOAD_AMA_MASTERFILE_TABLE')

    DAG.sequence('LOAD_AMA_MASTERFILE_TABLE')

    DAG.last('LOAD_AMA_MASTERFILE_TABLE') >> DAG.SYNC_PROFILES_TO_DATABASE
else:
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_ABMS >> DAG.CREATE_AGGREGATED_ABMS >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_DEA >> DAG.CREATE_AGGREGATED_DEA >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_DEMOG >> DAG.CREATE_AGGREGATED_DEMOG >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_LICENSE >> DAG.CREATE_AGGREGATED_LICENSES >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_MED_SCH >> DAG.CREATE_AGGREGATED_MED_SCH >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_MED_TRAIN >> DAG.CREATE_AGGREGATED_MED_TRAIN >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_NPI >> DAG.CREATE_AGGREGATED_NPI >> DAG.CREATE_AMA_PROFILE_TABLE
    DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES_SANCTIONS >> DAG.CREATE_AGGREGATED_SANCTIONS >> DAG.CREATE_AMA_PROFILE_TABLE

    DAG.CREATE_AMA_PROFILE_TABLE \
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
