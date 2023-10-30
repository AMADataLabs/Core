''' DAG definition for PROFILES '''
from datalabs import feature
from datalabs.etl.dag import dag
from datalabs.etl.dag.dag import Repeat
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
from datalabs.etl.manipulate.transform import SplitTransformerTask
from datalabs.etl.vericre.profile.load import VeriCreProfileSynchronizerTask
from datalabs.etl.sftp.extract import SFTPFileExtractorTask


@dag.register(name="VERICRE_PROFILES_ETL")
class DAG(dag.DAG):
    EXTRACT_AMA_PHYSICIAN_PROFILES: SFTPFileExtractorTask
    STANDARDIZE_ABMS_DATES: DateFormatTransformerTask
    STANDARDIZE_DEA_DATES: DateFormatTransformerTask
    STANDARDIZE_DEMOGRAPHICS_DATES: DateFormatTransformerTask
    STANDARDIZE_LICENSES_DATES: DateFormatTransformerTask
    STANDARDIZE_MEDICAL_SCHOOLS_DATES: DateFormatTransformerTask
    STANDARDIZE_MEDICAL_TRAINING_DATES: DateFormatTransformerTask
    STANDARDIZE_NPI_DATES: DateFormatTransformerTask
    STANDARDIZE_SANCTIONS_DATES: DateFormatTransformerTask
    SPLIT_DEMOGRAPHICS: SplitTransformerTask

    CREATE_DEMOGRAPHICS: Repeat("DemographicsTransformerTask", 3)
    CREATE_DEA: DeaTransformerTask
    CREATE_NPI: NPITransformerTask
    CREATE_MEDICAL_SCHOOLS: MedicalSchoolsTransformerTask
    CREATE_ABMS: ABMSTransformerTask
    CREATE_MEDICAL_TRAINING: MedicalTrainingTransformerTask
    CREATE_LICENSES: LicensesTransformerTask
    CREATE_SANCTIONS: SanctionsTransformerTask
    CREATE_AMA_PROFILE_TABLE: Repeat("AMAProfileTransformerTask", 3)
    CONVERT_AMA_MASTERFILE_TO_JSON: Repeat("JSONTransformerTask", 3)
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
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_ABMS_DATES
        >> DAG.CREATE_ABMS
    )
    DAG.fan_out('CREATE_ABMS', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_DEA_DATES
        >> DAG.CREATE_DEA
    )
    DAG.fan_out('CREATE_DEA', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_DEMOGRAPHICS_DATES
        >> DAG.SPLIT_DEMOGRAPHICS
    )
    DAG.fan_out('SPLIT_DEMOGRAPHICS', 'CREATE_DEMOGRAPHICS')
    DAG.parallel('CREATE_DEMOGRAPHICS', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_LICENSES_DATES
        >> DAG.CREATE_LICENSES
    )
    DAG.fan_out('CREATE_LICENSES', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_MEDICAL_SCHOOLS_DATES
        >> DAG.CREATE_MEDICAL_SCHOOLS
    )
    DAG.fan_out('CREATE_MEDICAL_SCHOOLS', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_MEDICAL_TRAINING_DATES
        >> DAG.CREATE_MEDICAL_TRAINING
    )
    DAG.fan_out('CREATE_MEDICAL_TRAINING', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_NPI_DATES
        >> DAG.CREATE_NPI
    )
    DAG.fan_out('CREATE_NPI', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_SANCTIONS_DATES
        >> DAG.CREATE_SANCTIONS
    )
    DAG.fan_out('CREATE_SANCTIONS', 'CREATE_AMA_PROFILE_TABLE')

    DAG.parallel('CREATE_AMA_PROFILE_TABLE', 'CONVERT_AMA_MASTERFILE_TO_JSON')

    DAG.parallel('CONVERT_AMA_MASTERFILE_TO_JSON', 'LOAD_AMA_MASTERFILE_TABLE')
    DAG.fan_in('LOAD_AMA_MASTERFILE_TABLE', 'SYNC_PROFILES_TO_DATABASE')

else:
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_ABMS_DATES
        >> DAG.CREATE_ABMS
    )
    DAG.fan_out('CREATE_ABMS', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_DEA_DATES
        >> DAG.CREATE_DEA
    )
    DAG.fan_out('CREATE_DEA', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_DEMOGRAPHICS_DATES
        >> DAG.SPLIT_DEMOGRAPHICS
    )
    DAG.fan_out('SPLIT_DEMOGRAPHICS', 'CREATE_DEMOGRAPHICS')
    DAG.parallel('CREATE_DEMOGRAPHICS', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_LICENSES_DATES
        >> DAG.CREATE_LICENSES
    )
    DAG.fan_out('CREATE_LICENSES', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_MEDICAL_SCHOOLS_DATES
        >> DAG.CREATE_MEDICAL_SCHOOLS
    )
    DAG.fan_out('CREATE_MEDICAL_SCHOOLS', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_MEDICAL_TRAINING_DATES
        >> DAG.CREATE_MEDICAL_TRAINING
    )
    DAG.fan_out('CREATE_MEDICAL_TRAINING', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_NPI_DATES
        >> DAG.CREATE_NPI
    )
    DAG.fan_out('CREATE_NPI', 'CREATE_AMA_PROFILE_TABLE')
    (
        DAG.EXTRACT_AMA_PHYSICIAN_PROFILES
        >> DAG.STANDARDIZE_SANCTIONS_DATES
        >> DAG.CREATE_SANCTIONS
    )
    DAG.fan_out('CREATE_SANCTIONS', 'CREATE_AMA_PROFILE_TABLE')

    DAG.parallel('CREATE_AMA_PROFILE_TABLE', 'CONVERT_AMA_MASTERFILE_TO_JSON')

    DAG.parallel('CONVERT_AMA_MASTERFILE_TO_JSON', 'LOAD_AMA_MASTERFILE_TABLE')

    DAG.sequence('LOAD_AMA_MASTERFILE_TABLE')

if feature.enabled("CAQH_PROFILES"):
    DAG.CREATE_AMA_PROFILE_TABLE \
        >> DAG.CREATE_CAQH_STATUS_URLS \
        >> DAG.EXTRACT_CAQH_PROFILE_STATUSES \
        >> DAG.CREATE_CAQH_PROFILE_URLS \
        >> DAG.EXTRACT_CAQH_PHYSICIAN_PROFILES \
        >> DAG.LOAD_CAQH_PROFILES_TO_LEDGER \
        >> DAG.SYNC_PROFILES_TO_DATABASE
