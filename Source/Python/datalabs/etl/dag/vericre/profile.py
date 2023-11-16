''' DAG definition for PROFILES '''
from datalabs import feature
from datalabs.etl.dag import dag
from datalabs.etl.http.extract import HTTPFileListExtractorTask
from datalabs.etl.manipulate.transform import DateFormatTransformerTask
from datalabs.etl.qldb.load import QLDBLoaderTask
from datalabs.etl.vericre.profile.transform import CAQHProfileURLListTranformerTask
from datalabs.etl.vericre.profile.transform import CAQHStatusURLListTransformerTask
from datalabs.etl.vericre.profile.transform import CAQHProfileTransformerTask
from datalabs.etl.vericre.profile.transform import DeaTransformerTask
from datalabs.etl.vericre.profile.transform import NPITransformerTask
from datalabs.etl.vericre.profile.transform import MedicalSchoolsTransformerTask
from datalabs.etl.vericre.profile.transform import ABMSTransformerTask
from datalabs.etl.vericre.profile.transform import MedicalTrainingTransformerTask
from datalabs.etl.vericre.profile.transform import LicensesTransformerTask
from datalabs.etl.vericre.profile.transform import SanctionsTransformerTask
from datalabs.etl.sftp.extract import SFTPFileExtractorTask


@dag.register(name="VERICRE_PROFILES_ETL")
class DAG(dag.DAG):
    EXTRACT_AMA_PHYSICIAN_PROFILES: SFTPFileExtractorTask
    STANDARDIZE_DATES: DateFormatTransformerTask

    CREATE_DEMOGRAPHICS: "datalabs.etl.vericre.profile.transform.DemographicsTransformerTask"
    CREATE_DEA: DeaTransformerTask
    CREATE_NPI: NPITransformerTask
    CREATE_MEDICAL_SCHOOLS: MedicalSchoolsTransformerTask
    CREATE_ABMS: ABMSTransformerTask
    CREATE_MEDICAL_TRAINING: MedicalTrainingTransformerTask
    CREATE_LICENSES: LicensesTransformerTask
    CREATE_SANCTIONS: SanctionsTransformerTask
    CREATE_AMA_PROFILE_TABLE: "datalabs.etl.vericre.profile.transform.AMAProfileTransformerTask"
    CONVERT_AMA_PROFILE_TO_JSON: "datalabs.etl.vericre.profile.transform.JSONTransformerTask"
    LOAD_AMA_PROFILE_TABLE: QLDBLoaderTask

    if feature.enabled("CAQH_PROFILES"):
        CREATE_CAQH_STATUS_URLS: CAQHStatusURLListTransformerTask
        EXTRACT_CAQH_PROFILE_STATUSES: HTTPFileListExtractorTask
        CREATE_CAQH_PROFILE_URLS: CAQHProfileURLListTranformerTask
        EXTRACT_CAQH_PHYSICIAN_PROFILES: HTTPFileListExtractorTask
        CREATE_CAQH_PROFILE_TABLE: CAQHProfileTransformerTask
        LOAD_CAQH_PROFILES_TO_LEDGER: QLDBLoaderTask


# pylint: disable=expression-not-assigned, pointless-statement
DAG.EXTRACT_AMA_PHYSICIAN_PROFILES >> DAG.STANDARDIZE_DATES
DAG.STANDARDIZE_DATES >> DAG.CREATE_DEMOGRAPHICS >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_ABMS >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_DEA >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_LICENSES >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_MEDICAL_SCHOOLS >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_MEDICAL_TRAINING >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_NPI >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.STANDARDIZE_DATES >> DAG.CREATE_SANCTIONS >> DAG.CREATE_AMA_PROFILE_TABLE
DAG.CREATE_AMA_PROFILE_TABLE >> DAG.CONVERT_AMA_PROFILE_TO_JSON >> DAG.LOAD_AMA_PROFILE_TABLE


if feature.enabled("CAQH_PROFILES"):
    (
        DAG.CREATE_AMA_PROFILE_TABLE
        >> DAG.CREATE_CAQH_STATUS_URLS
        >> DAG.EXTRACT_CAQH_PROFILE_STATUSES
        >> DAG.CREATE_CAQH_PROFILE_URLS
        >> DAG.EXTRACT_CAQH_PHYSICIAN_PROFILES
        >> DAG.LOAD_CAQH_PROFILES_TO_LEDGER
    )
