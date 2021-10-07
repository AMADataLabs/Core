''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.oneview.email.transform import PhysicianEmailStatusTransformer
# from   datalabs.etl.http.extract import HTTPFileExtractorTask
from   datalabs.etl.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.manipulate.transform import SplitTransformerTask
from   datalabs.etl.manipulate.transform import ConcatenateTransformerTask
from   datalabs.etl.oneview.credentialing.transform import \
    CredentialingTransformerTask, \
    CredentialingFinalTransformerTask, \
    CredentialingOrderPruningTransformerTask
from   datalabs.etl.oneview.historical_resident.transform import \
    HistoricalResidentTransformerTask, \
    HistoricalResidentPruningTransformerTask
from   datalabs.etl.oneview.iqvia.transform import \
    IQVIABusinessTransformerTask, \
    IQVIAProviderTransformerTask, \
    IQVIAProviderPruningTransformerTask, \
    IQVIAUpdateTransformerTask
# from   datalabs.etl.oneview.link.transform import
#     CredentialingCustomerInstitutionTransformerTask, CredentialingCustomerBusinessTransformerTask  # v2
from  datalabs.etl.oneview.link.transform import ResidencyProgramPhysicianTransformerTask
# from   datalabs.etl.oneview.melissa.transform import MelissaTransformerTask
# from   datalabs.etl.oneview.ppd.transform import PPDTransformerTask, NPITransformerTask
from   datalabs.etl.oneview.ppd.transform import PhysicianTransformerTask
# from   datalabs.etl.oneview.reference.transform import \
#     FederalInformationProcessingStandardCountyTransformerTask \
#     StateTransformerTask, \
#     SpecialtyMergeTransformerTask, \
#     MajorProfessionalActivityTransformerTask, \
#     CoreBasedStatisticalAreaTransformerTask, \
#     PresentEmploymentTransformerTask, \
#     TypeOfPracticeTransformerTask, \

# from   datalabs.etl.oneview.reference.transform import \
#     StaticReferenceTablesTransformerTask, \
#     ClassOfTradeTransformerTask, \
#     MedicalSchoolTransformerTask
from   datalabs.etl.oneview.residency.transform import ResidencyTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
# from   datalabs.etl.sftp.extract import SFTPIBM437TextFileExtractorTask
# from   datalabs.etl.transform import PassThroughTransformerTask


class OneViewDAG(DAG):
    # EXTRACT_PPD: SFTPIBM437TextFileExtractorTask
    # EXTRACT_PHYSICIAN_RACE_ETHNICITY: SFTPFileExtractorTask
    # EXTRACT_MEDICAL_STUDENT: SFTPFileExtractorTask
    # SUPPLEMENT_PPD_TABLE: PPDTransformerTask
    # SPLIT_PPD_TABLE: SplitTransformerTask
    #
    # EXTRACT_PARTY_KEYS_1: JDBCExtractorTask
    # EXTRACT_PARTY_KEYS_2: JDBCExtractorTask
    # EXTRACT_PARTY_KEYS_3: JDBCExtractorTask
    # CONCATENATE_PARTY_KEYS: ConcatenateTransformerTask
    # CREATE_PHYSICIAN_NPI_TABLE: NPITransformerTask
    #
    # EXTRACT_MEMBERSHIP_DATA: JDBCExtractorTask
    # EXTRACT_PHYSICIAN_EMAIL_STATUS_1: JDBCExtractorTask
    # EXTRACT_PHYSICIAN_EMAIL_STATUS_2: JDBCExtractorTask
    # EXTRACT_PHYSICIAN_EMAIL_STATUS_3: JDBCExtractorTask
    EXTRACT_PHYSICIAN_EMAIL_STATUS_4: JDBCExtractorTask
    EXTRACT_PHYSICIAN_EMAIL_STATUS_5: JDBCExtractorTask
    EXTRACT_PHYSICIAN_EMAIL_STATUS_6: JDBCExtractorTask
    CONCATENATE_PHYSICIAN_EMAIL_STATUS: ConcatenateTransformerTask
    CREATE_PHYSICIAN_EMAIL_STATUS_TABLE: PhysicianEmailStatusTransformer
    CREATE_PHYSICIAN_TABLE_1: PhysicianTransformerTask
    CREATE_PHYSICIAN_TABLE_2: PhysicianTransformerTask
    CREATE_PHYSICIAN_TABLE_3: PhysicianTransformerTask
    CREATE_PHYSICIAN_TABLE_4: PhysicianTransformerTask
    CREATE_PHYSICIAN_TABLE_5: PhysicianTransformerTask
    CREATE_PHYSICIAN_TABLE_6: PhysicianTransformerTask
    CONCATENATE_PHYSICIAN_TABLE: ConcatenateTransformerTask

    # EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY: HTTPFileExtractorTask
    # CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: \
    #     FederalInformationProcessingStandardCountyTransformerTask
    # LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: ORMLoaderTask
    #
    # EXTRACT_STATE: JDBCExtractorTask
    # CREATE_STATE_TABLE: StateTransformerTask
    # LOAD_STATE_TABLE: ORMLoaderTask
    #
    # EXTRACT_SPECIALTY: JDBCExtractorTask
    # CREATE_SPECIALTY_TABLE: PassThroughTransformerTask
    # LOAD_SPECIALTY_TABLE: ORMLoaderTask
    # REMOVE_UNUSED_SPECIALTIES: SpecialtyMergeTransformerTask
    #
    # EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY: JDBCExtractorTask
    # CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: MajorProfessionalActivityTransformerTask
    # LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: ORMLoaderTask
    #
    # EXTRACT_CORE_BASED_STATISTICAL_AREA: HTTPFileExtractorTask
    # CREATE_CORE_BASED_STATISTICAL_AREA_TABLE: CoreBasedStatisticalAreaTransformerTask
    # LOAD_CORE_BASED_STATISTICAL_AREA_TABLE: ORMLoaderTask
    #
    # EXTRACT_PRESENT_EMPLOYMENT: JDBCExtractorTask
    # CREATE_PRESENT_EMPLOYMENT_TABLE: PresentEmploymentTransformerTask
    # LOAD_PRESENT_EMPLOYMENT_TABLE: ORMLoaderTask
    #
    # EXTRACT_TYPE_OF_PRACTICE: JDBCExtractorTask
    # CREATE_TYPE_OF_PRACTICE_TABLE: TypeOfPracticeTransformerTask
    # LOAD_TYPE_OF_PRACTICE_TABLE: ORMLoaderTask

    LOAD_PHYSICIAN_TABLE_1: ORMLoaderTask
    LOAD_PHYSICIAN_TABLE_2: ORMLoaderTask
    LOAD_PHYSICIAN_TABLE_3: ORMLoaderTask
    LOAD_PHYSICIAN_TABLE_4: ORMLoaderTask
    LOAD_PHYSICIAN_TABLE_5: ORMLoaderTask
    LOAD_PHYSICIAN_TABLE_6: ORMLoaderTask

    # EXTRACT_RESIDENCY: SFTPFileExtractorTask
    CREATE_RESIDENCY_TABLES: ResidencyTransformerTask
    # LOAD_RESIDENCY_INSTITUTION_TABLE: ORMLoaderTask
    # LOAD_RESIDENCY_PROGRAM_TABLE: ORMLoaderTask
    # LOAD_RESIDENCY_PERSONNEL_TABLE: ORMLoaderTask

    CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE: ResidencyProgramPhysicianTransformerTask

    # EXTRACT_MELISSA: JDBCExtractorTask
    # CREATE_MELISSA_TABLES: MelissaTransformerTask
    # LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE: ORMLoaderTask
    # LOAD_COUNTY_TABLE: ORMLoaderTask
    # LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE: ORMLoaderTask
    # LOAD_ZIP_CODE_TABLE: ORMLoaderTask
    # LOAD_AREA_CODE_TABLE: ORMLoaderTask
    # LOAD_CENSUS_TABLE: ORMLoaderTask
    # LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE: ORMLoaderTask

    # EXTRACT_IQVIA_BUSINESS: JDBCExtractorTask
    # EXTRACT_IQVIA_PROVIDER: JDBCExtractorTask
    # EXTRACT_IQVIA_PROVIDER_AFFILIATION: JDBCExtractorTask
    CREATE_IQVIA_UPDATE_TABLE: IQVIAUpdateTransformerTask
    CREATE_BUSINESS_TABLE: IQVIABusinessTransformerTask
    CREATE_PROVIDER_TABLE: IQVIAProviderTransformerTask
    REMOVE_UNKNOWN_PROVIDERS: IQVIAProviderPruningTransformerTask
    SPLIT_IQVIA_BUSINESS_TABLE: SplitTransformerTask
    LOAD_IQVIA_BUSINESS_TABLE_1: ORMLoaderTask
    LOAD_IQVIA_BUSINESS_TABLE_2: ORMLoaderTask
    LOAD_IQVIA_BUSINESS_TABLE_3: ORMLoaderTask
    SPLIT_IQVIA_PROVIDER_TABLE: SplitTransformerTask
    LOAD_IQVIA_PROVIDER_TABLE_1: ORMLoaderTask
    LOAD_IQVIA_PROVIDER_TABLE_2: ORMLoaderTask
    LOAD_IQVIA_PROVIDER_TABLE_3: ORMLoaderTask
    LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE: ORMLoaderTask
    LOAD_IQVIA_UPDATE_TABLE: ORMLoaderTask

    EXTRACT_CREDENTIALING: SFTPFileExtractorTask
    EXTRACT_CREDENTIALING_ADDRESSES: SFTPFileExtractorTask
    CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES: CredentialingTransformerTask
    MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE: CredentialingFinalTransformerTask
    REMOVE_UNKNOWN_ORDERS: CredentialingOrderPruningTransformerTask
    SPLIT_CREDENTIALING_ORDER_TABLE: SplitTransformerTask

    LOAD_CREDENTIALING_CUSTOMER_PRODUCT_TABLES: ORMLoaderTask
    LOAD_CREDENTIALING_ORDER_TABLE_1: ORMLoaderTask
    LOAD_CREDENTIALING_ORDER_TABLE_2: ORMLoaderTask
    LOAD_CREDENTIALING_ORDER_TABLE_3: ORMLoaderTask

    # CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE: CredentialingCustomerInstitutionTransformerTask  # v2
    # CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE: CredentialingCustomerBusinessTransformerTask  # v2
    LOAD_LINKING_TABLES: ORMLoaderTask

    EXTRACT_HISTORICAL_RESIDENT: SFTPFileExtractorTask
    CREATE_HISTORICAL_RESIDENT_TABLE: HistoricalResidentTransformerTask
    REMOVE_UNKNOWN_HISTORICAL_RESIDENTS: HistoricalResidentPruningTransformerTask
    SPLIT_HISTORICAL_RESIDENT_TABLE: SplitTransformerTask
    LOAD_HISTORICAL_RESIDENT_TABLE_1: ORMLoaderTask
    LOAD_HISTORICAL_RESIDENT_TABLE_2: ORMLoaderTask
    LOAD_HISTORICAL_RESIDENT_TABLE_3: ORMLoaderTask
    LOAD_HISTORICAL_RESIDENT_TABLE_4: ORMLoaderTask
    LOAD_HISTORICAL_RESIDENT_TABLE_5: ORMLoaderTask
    LOAD_HISTORICAL_RESIDENT_TABLE_6: ORMLoaderTask

    # EXTRACT_CLASS_OF_TRADE: JDBCExtractorTask
    # CREATE_STATIC_REFERENCE_TABLE: StaticReferenceTablesTransformerTask
    # CREATE_CLASS_OF_TRADE_TABLE: ClassOfTradeTransformerTask
    # LOAD_CLASS_OF_TRADE_TABLE: ORMLoaderTask
    # LOAD_STATIC_REFERENCE_TABLE: ORMLoaderTask
    # EXTRACT_MEDICAL_SCHOOL: JDBCExtractorTask
    # CREATE_MEDICAL_SCHOOL_TABLE: MedicalSchoolTransformerTask
    # LOAD_MEDICAL_SCHOOL_TABLE: ORMLoaderTask


# pylint: disable=pointless-statement
# OneViewDAG.EXTRACT_PPD >> OneViewDAG.SUPPLEMENT_PPD_TABLE
# OneViewDAG.EXTRACT_PHYSICIAN_RACE_ETHNICITY >> OneViewDAG.SUPPLEMENT_PPD_TABLE
# OneViewDAG.EXTRACT_MEDICAL_STUDENT >> OneViewDAG.SUPPLEMENT_PPD_TABLE
# OneViewDAG.SUPPLEMENT_PPD_TABLE >> OneViewDAG.SPLIT_PPD_TABLE
#
# OneViewDAG.EXTRACT_PARTY_KEYS_1 >> OneViewDAG.EXTRACT_PARTY_KEYS_2 >> OneViewDAG.EXTRACT_PARTY_KEYS_3 \
#     >> OneViewDAG.CONCATENATE_PARTY_KEYS >> OneViewDAG.CREATE_PHYSICIAN_NPI_TABLE
# OneViewDAG.SPLIT_PPD_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_1
# OneViewDAG.CREATE_PHYSICIAN_NPI_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_1
# OneViewDAG.EXTRACT_MEMBERSHIP_DATA >> OneViewDAG.CREATE_PHYSICIAN_TABLE_1

# OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS_1 \
#     >> OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS_2 \
#     >> OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS_3 \
OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS_4 \
    >> OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS_5 \
    >> OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS_6 \
    >> OneViewDAG.CONCATENATE_PHYSICIAN_EMAIL_STATUS \
    >> OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE

OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_1
OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_2
OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_3
OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_4
OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_5
OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE_6

OneViewDAG.CREATE_PHYSICIAN_TABLE_1 >> OneViewDAG.CONCATENATE_PHYSICIAN_TABLE
OneViewDAG.CREATE_PHYSICIAN_TABLE_2 >> OneViewDAG.CONCATENATE_PHYSICIAN_TABLE
OneViewDAG.CREATE_PHYSICIAN_TABLE_3 >> OneViewDAG.CONCATENATE_PHYSICIAN_TABLE
OneViewDAG.CREATE_PHYSICIAN_TABLE_4 >> OneViewDAG.CONCATENATE_PHYSICIAN_TABLE
OneViewDAG.CREATE_PHYSICIAN_TABLE_5 >> OneViewDAG.CONCATENATE_PHYSICIAN_TABLE
OneViewDAG.CREATE_PHYSICIAN_TABLE_6 >> OneViewDAG.CONCATENATE_PHYSICIAN_TABLE

# OneViewDAG.EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY \
#     >> OneViewDAG.CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE \
#     >> OneViewDAG.LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE

# OneViewDAG.EXTRACT_STATE >> OneViewDAG.CREATE_STATE_TABLE >> OneViewDAG.LOAD_STATE_TABLE
#
# OneViewDAG.EXTRACT_SPECIALTY >> OneViewDAG.CREATE_SPECIALTY_TABLE >> OneViewDAG.REMOVE_UNUSED_SPECIALTIES
# OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNUSED_SPECIALTIES
# OneViewDAG.REMOVE_UNUSED_SPECIALTIES >> OneViewDAG.LOAD_SPECIALTY_TABLE
#
# OneViewDAG.EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY >> OneViewDAG.CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE \
#     >> OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE
#
# OneViewDAG.EXTRACT_CORE_BASED_STATISTICAL_AREA \
#     >> OneViewDAG.CREATE_CORE_BASED_STATISTICAL_AREA_TABLE \
#     >> OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE
#
# OneViewDAG.EXTRACT_PRESENT_EMPLOYMENT \
#     >> OneViewDAG.CREATE_PRESENT_EMPLOYMENT_TABLE \
#     >> OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE
#
# OneViewDAG.EXTRACT_TYPE_OF_PRACTICE \
#     >> OneViewDAG.CREATE_TYPE_OF_PRACTICE_TABLE \
#     >> OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE
#
OneViewDAG.CREATE_PHYSICIAN_TABLE_1 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
OneViewDAG.CREATE_PHYSICIAN_TABLE_2 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_2
OneViewDAG.CREATE_PHYSICIAN_TABLE_3 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_3
OneViewDAG.CREATE_PHYSICIAN_TABLE_4 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_4
OneViewDAG.CREATE_PHYSICIAN_TABLE_5 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_5
OneViewDAG.CREATE_PHYSICIAN_TABLE_6 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_6
# OneViewDAG.LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
# OneViewDAG.LOAD_STATE_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
# OneViewDAG.LOAD_SPECIALTY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
# OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
# OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
# OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1
# OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE_1

OneViewDAG.LOAD_PHYSICIAN_TABLE_1 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_2 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_3 >> \
OneViewDAG.LOAD_PHYSICIAN_TABLE_4 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_5 >> OneViewDAG.LOAD_PHYSICIAN_TABLE_6
#
# OneViewDAG.EXTRACT_RESIDENCY >> OneViewDAG.CREATE_RESIDENCY_TABLES \
#     >> OneViewDAG.LOAD_RESIDENCY_INSTITUTION_TABLE \
#     >> OneViewDAG.LOAD_RESIDENCY_PROGRAM_TABLE \
#     >> OneViewDAG.LOAD_RESIDENCY_PERSONNEL_TABLE

OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE
OneViewDAG.CREATE_RESIDENCY_TABLES >> OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE

# OneViewDAG.EXTRACT_MELISSA >> OneViewDAG.CREATE_MELISSA_TABLES
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_AREA_CODE_TABLE
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_CENSUS_TABLE
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_COUNTY_TABLE
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE
# OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_ZIP_CODE_TABLE

# OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE >> OneViewDAG.LOAD_LINKING_TABLES
# OneViewDAG.LOAD_RESIDENCY_PERSONNEL_TABLE >> OneViewDAG.LOAD_LINKING_TABLES
# OneViewDAG.LOAD_PHYSICIAN_TABLE_6 >> OneViewDAG.LOAD_LINKING_TABLES

# OneViewDAG.EXTRACT_IQVIA_BUSINESS >> OneViewDAG.CREATE_BUSINESS_TABLE
# OneViewDAG.EXTRACT_IQVIA_BUSINESS >> OneViewDAG.CREATE_IQVIA_UPDATE_TABLE

OneViewDAG.CREATE_IQVIA_UPDATE_TABLE >> OneViewDAG.LOAD_IQVIA_UPDATE_TABLE

OneViewDAG.CREATE_BUSINESS_TABLE >> OneViewDAG.SPLIT_IQVIA_BUSINESS_TABLE

# OneViewDAG.LOAD_STATIC_REFERENCE_TABLE >> OneViewDAG.LOAD_IQVIA_BUSINESS_TABLE_1
OneViewDAG.LOAD_IQVIA_UPDATE_TABLE >> OneViewDAG.LOAD_IQVIA_BUSINESS_TABLE_1

OneViewDAG.SPLIT_IQVIA_BUSINESS_TABLE \
    >> OneViewDAG.LOAD_IQVIA_BUSINESS_TABLE_1 \
    >> OneViewDAG.LOAD_IQVIA_BUSINESS_TABLE_2 \
    >> OneViewDAG.LOAD_IQVIA_BUSINESS_TABLE_3

# OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.CREATE_PROVIDER_TABLE
# OneViewDAG.EXTRACT_IQVIA_PROVIDER >> OneViewDAG.CREATE_PROVIDER_TABLE
# OneViewDAG.EXTRACT_IQVIA_PROVIDER_AFFILIATION >> OneViewDAG.CREATE_PROVIDER_TABLE

OneViewDAG.CREATE_PROVIDER_TABLE >> OneViewDAG.REMOVE_UNKNOWN_PROVIDERS
OneViewDAG.REMOVE_UNKNOWN_PROVIDERS >> OneViewDAG.SPLIT_IQVIA_PROVIDER_TABLE
OneViewDAG.LOAD_PHYSICIAN_TABLE_6 >> OneViewDAG.LOAD_IQVIA_PROVIDER_TABLE_1
OneViewDAG.LOAD_IQVIA_UPDATE_TABLE >> OneViewDAG.LOAD_IQVIA_PROVIDER_TABLE_1

OneViewDAG.SPLIT_IQVIA_PROVIDER_TABLE \
    >> OneViewDAG.LOAD_IQVIA_PROVIDER_TABLE_1 \
    >> OneViewDAG.LOAD_IQVIA_PROVIDER_TABLE_2 \
    >> OneViewDAG.LOAD_IQVIA_PROVIDER_TABLE_3

OneViewDAG.LOAD_PHYSICIAN_TABLE_6 >> OneViewDAG.LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE
OneViewDAG.LOAD_IQVIA_BUSINESS_TABLE_3 >> OneViewDAG.LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE
OneViewDAG.LOAD_IQVIA_PROVIDER_TABLE_3 >> OneViewDAG.LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE
OneViewDAG.LOAD_IQVIA_UPDATE_TABLE >> OneViewDAG.LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE

OneViewDAG.EXTRACT_CREDENTIALING >> OneViewDAG.EXTRACT_CREDENTIALING_ADDRESSES \
    >> OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE
OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> OneViewDAG.LOAD_CREDENTIALING_CUSTOMER_PRODUCT_TABLES
OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> OneViewDAG.REMOVE_UNKNOWN_ORDERS
OneViewDAG.REMOVE_UNKNOWN_ORDERS \
    >> OneViewDAG.SPLIT_CREDENTIALING_ORDER_TABLE \
    >> OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE_1
OneViewDAG.LOAD_PHYSICIAN_TABLE_6 >> OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE_1

OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE_1 >> OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE_2 \
    >> OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE_3


# OneViewDAG.EXTRACT_HISTORICAL_RESIDENT \
#     >> OneViewDAG.CREATE_HISTORICAL_RESIDENT_TABLE \
#     >> OneViewDAG.REMOVE_UNKNOWN_HISTORICAL_RESIDENTS \
#     >> OneViewDAG.SPLIT_HISTORICAL_RESIDENT_TABLE
OneViewDAG.LOAD_PHYSICIAN_TABLE_6 >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_1

OneViewDAG.SPLIT_HISTORICAL_RESIDENT_TABLE >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_1
OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_1 >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_2 \
    >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_3 >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_4 \
    >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_5 >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE_6

# OneViewDAG.CREATE_STATIC_REFERENCE_TABLE >> OneViewDAG.LOAD_STATIC_REFERENCE_TABLE
#
# OneViewDAG.EXTRACT_CLASS_OF_TRADE >> OneViewDAG.CREATE_CLASS_OF_TRADE_TABLE \
#     >> OneViewDAG.LOAD_CLASS_OF_TRADE_TABLE

# OneViewDAG.EXTRACT_MEDICAL_SCHOOL >> OneViewDAG.CREATE_MEDICAL_SCHOOL_TABLE \
#     >> OneViewDAG.LOAD_MEDICAL_SCHOOL_TABLE
