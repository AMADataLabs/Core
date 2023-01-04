''' DAG definition for the OneView ETL. '''
from   datalabs.etl.dag.dag import DAG, register, Repeat
from   datalabs.etl.oneview.email.transform import PhysicianEmailStatusTransformer
from   datalabs.etl.http.extract import HTTPFileExtractorTask
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
from   datalabs.etl.oneview.melissa.transform import MelissaTransformerTask
from   datalabs.etl.oneview.ppd.transform import PPDTransformerTask, NPITransformerTask
from   datalabs.etl.oneview.ppd.transform import PhysicianTransformerTask
from   datalabs.etl.oneview.reference.transform import \
    FederalInformationProcessingStandardCountyTransformerTask, \
    StateTransformerTask, \
    SpecialtyMergeTransformerTask, \
    MajorProfessionalActivityTransformerTask, \
    CoreBasedStatisticalAreaTransformerTask, \
    PresentEmploymentTransformerTask, \
    TypeOfPracticeTransformerTask \

from   datalabs.etl.oneview.reference.transform import \
    StaticReferenceTablesTransformerTask, \
    ClassOfTradeTransformerTask, \
    MedicalSchoolTransformerTask
from   datalabs.etl.oneview.residency.transform import ResidencyTransformerTask
from   datalabs.etl.oneview.medical_licenses.transform import MedicalLicensesCleanerTask, MedicalLicensesTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask, MaterializedViewRefresherTask, ReindexerTask
from   datalabs.etl.s3.extract import S3FileExtractorTask
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask
from   datalabs.etl.sftp.extract import SFTPIBM437TextFileExtractorTask
from   datalabs.etl.transform import PassThroughTransformerTask


@register(name="ONEVIEW")
class OneViewDAG(DAG):
    EXTRACT_PPD: SFTPIBM437TextFileExtractorTask
    EXTRACT_PHYSICIAN_RACE_ETHNICITY: SFTPFileExtractorTask
    EXTRACT_MEDICAL_STUDENT: SFTPFileExtractorTask
    SUPPLEMENT_PPD_TABLE: PPDTransformerTask
    SPLIT_PPD_TABLE: SplitTransformerTask

    EXTRACT_PARTY_KEYS: Repeat("SqlExtractorTask", 3)
    CONCATENATE_PARTY_KEYS: ConcatenateTransformerTask
    CREATE_PHYSICIAN_NPI_TABLE: NPITransformerTask

    EXTRACT_MEMBERSHIP_DATA: "SqlExtractorTask"
    EXTRACT_PHYSICIAN_EMAIL_STATUS: "SqlExtractorTask"
    CREATE_PHYSICIAN_EMAIL_STATUS_TABLE: PhysicianEmailStatusTransformer
    CREATE_PHYSICIAN_TABLE: Repeat(PhysicianTransformerTask, 10)
    CONCATENATE_PHYSICIAN_TABLE: ConcatenateTransformerTask

    EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY: HTTPFileExtractorTask
    EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE_SUPPLEMENT: S3FileExtractorTask
    CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: \
        FederalInformationProcessingStandardCountyTransformerTask
    SUPPLEMENT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: ConcatenateTransformerTask
    LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: ORMLoaderTask

    EXTRACT_STATE: "SqlExtractorTask"
    CREATE_STATE_TABLE: StateTransformerTask
    LOAD_STATE_TABLE: ORMLoaderTask

    EXTRACT_SPECIALTY: "SqlExtractorTask"
    CREATE_SPECIALTY_TABLE: PassThroughTransformerTask
    LOAD_SPECIALTY_TABLE: ORMLoaderTask
    REMOVE_UNUSED_SPECIALTIES: SpecialtyMergeTransformerTask

    EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY: "SqlExtractorTask"
    CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: MajorProfessionalActivityTransformerTask
    LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: ORMLoaderTask

    EXTRACT_CORE_BASED_STATISTICAL_AREA: S3FileExtractorTask
    CREATE_CORE_BASED_STATISTICAL_AREA_TABLE: CoreBasedStatisticalAreaTransformerTask
    LOAD_CORE_BASED_STATISTICAL_AREA_TABLE: ORMLoaderTask

    EXTRACT_PRESENT_EMPLOYMENT: "SqlExtractorTask"
    CREATE_PRESENT_EMPLOYMENT_TABLE: PresentEmploymentTransformerTask
    LOAD_PRESENT_EMPLOYMENT_TABLE: ORMLoaderTask

    EXTRACT_TYPE_OF_PRACTICE: "SqlExtractorTask"
    CREATE_TYPE_OF_PRACTICE_TABLE: TypeOfPracticeTransformerTask
    LOAD_TYPE_OF_PRACTICE_TABLE: ORMLoaderTask

    LOAD_PHYSICIAN_TABLE: ORMLoaderTask
    PRUNE_PHYSICIAN_TABLE: ORMLoaderTask

    EXTRACT_RESIDENCY: SFTPFileExtractorTask
    CREATE_RESIDENCY_TABLES: ResidencyTransformerTask
    LOAD_RESIDENCY_INSTITUTION_TABLE: ORMLoaderTask
    LOAD_RESIDENCY_PROGRAM_TABLE: ORMLoaderTask
    LOAD_RESIDENCY_PERSONNEL_TABLE: ORMLoaderTask

    CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE: ResidencyProgramPhysicianTransformerTask

    EXTRACT_MELISSA: "SqlExtractorTask"
    CREATE_MELISSA_TABLES: MelissaTransformerTask
    LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE: ORMLoaderTask
    LOAD_COUNTY_TABLE: ORMLoaderTask
    LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE: ORMLoaderTask
    LOAD_ZIP_CODE_TABLE: ORMLoaderTask
    LOAD_AREA_CODE_TABLE: ORMLoaderTask
    LOAD_CENSUS_TABLE: ORMLoaderTask
    LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE: ORMLoaderTask

    EXTRACT_IQVIA_BUSINESS: Repeat("SqlExtractorTask", 6)
    CREATE_BUSINESS_TABLE: Repeat(IQVIABusinessTransformerTask, 6)
    CREATE_IQVIA_UPDATE_TABLE: IQVIAUpdateTransformerTask
    CONCATENATE_BUSINESS_TABLE: ConcatenateTransformerTask
    LOAD_BUSINESS_TABLE: Repeat(ORMLoaderTask, 6)
    EXTRACT_IQVIA_PROVIDER: "SqlExtractorTask"
    EXTRACT_IQVIA_PROVIDER_AFFILIATION: "SqlExtractorTask"
    EXTRACT_IQVIA_BEST_PROVIDER_AFFILIATION: "SqlExtractorTask"
    CREATE_PROVIDER_TABLE: IQVIAProviderTransformerTask
    REMOVE_UNKNOWN_PROVIDERS: IQVIAProviderPruningTransformerTask
    SPLIT_IQVIA_PROVIDER_TABLE: SplitTransformerTask
    SPLIT_IQVIA_PROVIDER_AFFILIATION_TABLE: SplitTransformerTask
    LOAD_IQVIA_PROVIDER_TABLE: Repeat(ORMLoaderTask, 3)
    LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE: Repeat(ORMLoaderTask, 6)
    LOAD_IQVIA_UPDATE_TABLE: ORMLoaderTask

    EXTRACT_CREDENTIALING_CUSTOMER: "SqlExtractorTask"
    EXTRACT_CREDENTIALING_PRODUCT: "SqlExtractorTask"
    EXTRACT_CREDENTIALING_ORDER_YEARS: "SqlExtractorTask"
    EXTRACT_CREDENTIALING_ORDER: Repeat("SqlParametricExtractorTask", 9)
    EXTRACT_CREDENTIALING_ADDRESSES: SFTPFileExtractorTask
    CONCATENATE_CREDENTIALING_ORDER: ConcatenateTransformerTask
    CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES: CredentialingTransformerTask
    MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE: CredentialingFinalTransformerTask
    REMOVE_UNKNOWN_ORDERS: CredentialingOrderPruningTransformerTask
    SPLIT_CREDENTIALING_ORDER_TABLE: SplitTransformerTask

    LOAD_CREDENTIALING_CUSTOMER_TABLE: ORMLoaderTask
    LOAD_CREDENTIALING_PRODUCT_TABLE: ORMLoaderTask
    LOAD_CREDENTIALING_ORDER_TABLE: Repeat(ORMLoaderTask, 12)

    # CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE: CredentialingCustomerInstitutionTransformerTask  # v2
    # CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE: CredentialingCustomerBusinessTransformerTask  # v2
    LOAD_LINKING_TABLES: ORMLoaderTask

    EXTRACT_HISTORICAL_RESIDENT: SFTPFileExtractorTask
    CREATE_HISTORICAL_RESIDENT_TABLE: HistoricalResidentTransformerTask
    REMOVE_UNKNOWN_HISTORICAL_RESIDENTS: HistoricalResidentPruningTransformerTask
    SPLIT_HISTORICAL_RESIDENT_TABLE: SplitTransformerTask
    LOAD_HISTORICAL_RESIDENT_TABLE: Repeat(ORMLoaderTask, 6)

    EXTRACT_CLASS_OF_TRADE: "SqlExtractorTask"
    CREATE_STATIC_REFERENCE_TABLE: StaticReferenceTablesTransformerTask
    CREATE_CLASS_OF_TRADE_TABLE: ClassOfTradeTransformerTask
    LOAD_CLASS_OF_TRADE_TABLE: ORMLoaderTask
    LOAD_STATIC_REFERENCE_TABLE: ORMLoaderTask
    EXTRACT_MEDICAL_SCHOOL: "SqlExtractorTask"
    CREATE_MEDICAL_SCHOOL_TABLE: MedicalSchoolTransformerTask
    LOAD_MEDICAL_SCHOOL_TABLE: ORMLoaderTask

    EXTRACT_MEDICAL_LICENSES: "SqlExtractorTask"
    CLEAN_MEDICAL_LICENSES: MedicalLicensesCleanerTask
    CREATE_MEDICAL_LICENSES_TABLE: MedicalLicensesTransformerTask
    LOAD_MEDICAL_LICENSES_TABLE: ORMLoaderTask

    # The refresh tasks will be run using AWS Batch instead of Lambda
    REFRESH_PHYSICIAN_VIEW: MaterializedViewRefresherTask
    REINDEX_PHYSICIAN_VIEW: ReindexerTask
    REFRESH_PROVIDER_VIEW: MaterializedViewRefresherTask
    REINDEX_PROVIDER_VIEW: ReindexerTask


# pylint: disable=pointless-statement, expression-not-assigned
OneViewDAG.EXTRACT_PPD >> OneViewDAG.SUPPLEMENT_PPD_TABLE
OneViewDAG.EXTRACT_PHYSICIAN_RACE_ETHNICITY >> OneViewDAG.SUPPLEMENT_PPD_TABLE
OneViewDAG.EXTRACT_MEDICAL_STUDENT >> OneViewDAG.SUPPLEMENT_PPD_TABLE
OneViewDAG.SUPPLEMENT_PPD_TABLE >> OneViewDAG.SPLIT_PPD_TABLE

OneViewDAG.sequence('EXTRACT_PARTY_KEYS')
OneViewDAG.last('EXTRACT_PARTY_KEYS') \
    >> OneViewDAG.CONCATENATE_PARTY_KEYS \
    >> OneViewDAG.CREATE_PHYSICIAN_NPI_TABLE
OneViewDAG.CREATE_PHYSICIAN_NPI_TABLE >> OneViewDAG.first('CREATE_PHYSICIAN_TABLE')
OneViewDAG.EXTRACT_MEMBERSHIP_DATA >> OneViewDAG.first('CREATE_PHYSICIAN_TABLE')
OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE >> OneViewDAG.first('CREATE_PHYSICIAN_TABLE')

OneViewDAG.EXTRACT_PHYSICIAN_EMAIL_STATUS >> OneViewDAG.CREATE_PHYSICIAN_EMAIL_STATUS_TABLE

OneViewDAG.fan_out('CREATE_PHYSICIAN_EMAIL_STATUS_TABLE', 'CREATE_PHYSICIAN_TABLE')
OneViewDAG.fan_out('SPLIT_PPD_TABLE', 'CREATE_PHYSICIAN_TABLE')
OneViewDAG.fan_out('CREATE_PHYSICIAN_NPI_TABLE', 'CREATE_PHYSICIAN_TABLE')
OneViewDAG.fan_in('CREATE_PHYSICIAN_TABLE', 'CONCATENATE_PHYSICIAN_TABLE')

OneViewDAG.EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY \
    >> OneViewDAG.CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE \
    >> OneViewDAG.SUPPLEMENT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE \
    >> OneViewDAG.LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE

OneViewDAG.EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE_SUPPLEMENT\
    >> OneViewDAG.SUPPLEMENT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE

OneViewDAG.EXTRACT_STATE >> OneViewDAG.CREATE_STATE_TABLE >> OneViewDAG.LOAD_STATE_TABLE

OneViewDAG.EXTRACT_SPECIALTY >> OneViewDAG.CREATE_SPECIALTY_TABLE >> OneViewDAG.REMOVE_UNUSED_SPECIALTIES
OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNUSED_SPECIALTIES
OneViewDAG.REMOVE_UNUSED_SPECIALTIES >> OneViewDAG.LOAD_SPECIALTY_TABLE

OneViewDAG.EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY >> OneViewDAG.CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE \
    >> OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE

OneViewDAG.EXTRACT_CORE_BASED_STATISTICAL_AREA \
    >> OneViewDAG.CREATE_CORE_BASED_STATISTICAL_AREA_TABLE \
    >> OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE

OneViewDAG.EXTRACT_PRESENT_EMPLOYMENT \
    >> OneViewDAG.CREATE_PRESENT_EMPLOYMENT_TABLE \
    >> OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE

OneViewDAG.EXTRACT_TYPE_OF_PRACTICE \
    >> OneViewDAG.CREATE_TYPE_OF_PRACTICE_TABLE \
    >> OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE


OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_STATE_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_SPECIALTY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE

OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.PRUNE_PHYSICIAN_TABLE

OneViewDAG.EXTRACT_RESIDENCY >> OneViewDAG.CREATE_RESIDENCY_TABLES \
    >> OneViewDAG.LOAD_RESIDENCY_INSTITUTION_TABLE \
    >> OneViewDAG.LOAD_RESIDENCY_PROGRAM_TABLE \
    >> OneViewDAG.LOAD_RESIDENCY_PERSONNEL_TABLE

OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE
OneViewDAG.CREATE_RESIDENCY_TABLES >> OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE

OneViewDAG.EXTRACT_MELISSA >> OneViewDAG.CREATE_MELISSA_TABLES
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_AREA_CODE_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_CENSUS_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_COUNTY_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_ZIP_CODE_TABLE

OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE >> OneViewDAG.LOAD_LINKING_TABLES
OneViewDAG.LOAD_RESIDENCY_PERSONNEL_TABLE >> OneViewDAG.LOAD_LINKING_TABLES
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.LOAD_LINKING_TABLES

OneViewDAG.sequence('EXTRACT_IQVIA_BUSINESS')
OneViewDAG.parallel('EXTRACT_IQVIA_BUSINESS', 'CREATE_BUSINESS_TABLE')
OneViewDAG.fan_in('CREATE_BUSINESS_TABLE', 'CONCATENATE_BUSINESS_TABLE')

OneViewDAG.first('EXTRACT_IQVIA_BUSINESS') \
    >> OneViewDAG.CREATE_IQVIA_UPDATE_TABLE \
    >> OneViewDAG.LOAD_IQVIA_UPDATE_TABLE

OneViewDAG.LOAD_STATIC_REFERENCE_TABLE >> OneViewDAG.first('LOAD_BUSINESS_TABLE')

OneViewDAG.fan_out('CREATE_CLASS_OF_TRADE_TABLE', 'CREATE_BUSINESS_TABLE')

OneViewDAG.CONCATENATE_BUSINESS_TABLE >> OneViewDAG.first('LOAD_BUSINESS_TABLE')
OneViewDAG.sequence('LOAD_BUSINESS_TABLE')

OneViewDAG.EXTRACT_IQVIA_PROVIDER >> OneViewDAG.CREATE_PROVIDER_TABLE
OneViewDAG.EXTRACT_IQVIA_PROVIDER_AFFILIATION >> OneViewDAG.CREATE_PROVIDER_TABLE
OneViewDAG.EXTRACT_IQVIA_BEST_PROVIDER_AFFILIATION >> OneViewDAG.CREATE_PROVIDER_TABLE

OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNKNOWN_PROVIDERS
OneViewDAG.CONCATENATE_BUSINESS_TABLE >> OneViewDAG.REMOVE_UNKNOWN_PROVIDERS
OneViewDAG.CREATE_PROVIDER_TABLE >> OneViewDAG.REMOVE_UNKNOWN_PROVIDERS
OneViewDAG.REMOVE_UNKNOWN_PROVIDERS >> OneViewDAG.SPLIT_IQVIA_PROVIDER_TABLE
OneViewDAG.REMOVE_UNKNOWN_PROVIDERS >> OneViewDAG.SPLIT_IQVIA_PROVIDER_AFFILIATION_TABLE
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_TABLE')
OneViewDAG.LOAD_IQVIA_UPDATE_TABLE >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_TABLE')

OneViewDAG.SPLIT_IQVIA_PROVIDER_TABLE >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_TABLE')
OneViewDAG.sequence('LOAD_IQVIA_PROVIDER_TABLE')

OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE')
OneViewDAG.last('LOAD_IQVIA_PROVIDER_TABLE') >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE')
OneViewDAG.last('LOAD_BUSINESS_TABLE') >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE')
OneViewDAG.SPLIT_IQVIA_PROVIDER_AFFILIATION_TABLE >> OneViewDAG.first('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE')
OneViewDAG.sequence('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE')

OneViewDAG.EXTRACT_CREDENTIALING_CUSTOMER >> OneViewDAG.EXTRACT_CREDENTIALING_ADDRESSES \
    >> OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE
OneViewDAG.EXTRACT_CREDENTIALING_CUSTOMER >> OneViewDAG.CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES
OneViewDAG.EXTRACT_CREDENTIALING_PRODUCT >> OneViewDAG.CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES

OneViewDAG.fan_out('EXTRACT_CREDENTIALING_ORDER_YEARS', 'EXTRACT_CREDENTIALING_ORDER')
OneViewDAG.sequence('EXTRACT_CREDENTIALING_ORDER')
OneViewDAG.last('EXTRACT_CREDENTIALING_ORDER') >> OneViewDAG.CONCATENATE_CREDENTIALING_ORDER \
    >> OneViewDAG.CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES

OneViewDAG.CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES \
    >> OneViewDAG.LOAD_CREDENTIALING_CUSTOMER_TABLE >> OneViewDAG.LOAD_CREDENTIALING_PRODUCT_TABLE
OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> OneViewDAG.LOAD_CREDENTIALING_CUSTOMER_TABLE \
    >> OneViewDAG.LOAD_CREDENTIALING_PRODUCT_TABLE

OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNKNOWN_ORDERS
OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> OneViewDAG.REMOVE_UNKNOWN_ORDERS
OneViewDAG.CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES >> OneViewDAG.REMOVE_UNKNOWN_ORDERS
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNKNOWN_ORDERS
OneViewDAG.REMOVE_UNKNOWN_ORDERS \
    >> OneViewDAG.SPLIT_CREDENTIALING_ORDER_TABLE \
    >> OneViewDAG.first('LOAD_CREDENTIALING_ORDER_TABLE')
OneViewDAG.sequence('LOAD_CREDENTIALING_ORDER_TABLE')
OneViewDAG.LOAD_CREDENTIALING_PRODUCT_TABLE >> OneViewDAG.first('LOAD_CREDENTIALING_ORDER_TABLE')

OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNKNOWN_HISTORICAL_RESIDENTS
OneViewDAG.EXTRACT_HISTORICAL_RESIDENT \
    >> OneViewDAG.CREATE_HISTORICAL_RESIDENT_TABLE \
    >> OneViewDAG.REMOVE_UNKNOWN_HISTORICAL_RESIDENTS \
    >> OneViewDAG.SPLIT_HISTORICAL_RESIDENT_TABLE

OneViewDAG.SPLIT_HISTORICAL_RESIDENT_TABLE >> OneViewDAG.first('LOAD_HISTORICAL_RESIDENT_TABLE')
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.first('LOAD_HISTORICAL_RESIDENT_TABLE')
OneViewDAG.sequence('LOAD_HISTORICAL_RESIDENT_TABLE')

OneViewDAG.CREATE_STATIC_REFERENCE_TABLE >> OneViewDAG.LOAD_STATIC_REFERENCE_TABLE

OneViewDAG.EXTRACT_CLASS_OF_TRADE >> OneViewDAG.CREATE_CLASS_OF_TRADE_TABLE \
    >> OneViewDAG.LOAD_CLASS_OF_TRADE_TABLE

OneViewDAG.EXTRACT_MEDICAL_SCHOOL >> OneViewDAG.CREATE_MEDICAL_SCHOOL_TABLE \
    >> OneViewDAG.LOAD_MEDICAL_SCHOOL_TABLE

OneViewDAG.EXTRACT_MEDICAL_LICENSES >> OneViewDAG.CLEAN_MEDICAL_LICENSES >> OneViewDAG.CREATE_MEDICAL_LICENSES_TABLE \
    >> OneViewDAG.LOAD_MEDICAL_LICENSES_TABLE
OneViewDAG.CONCATENATE_PHYSICIAN_TABLE >> OneViewDAG.CREATE_MEDICAL_LICENSES_TABLE
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.LOAD_MEDICAL_LICENSES_TABLE

### Save for AWS Batch implementation of refresh tasks ###
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.REINDEX_PHYSICIAN_VIEW
OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.fan_in('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE', 'REFRESH_PHYSICIAN_VIEW')
OneViewDAG.fan_in('LOAD_BUSINESS_TABLE', 'REFRESH_PHYSICIAN_VIEW')
OneViewDAG.LOAD_SPECIALTY_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_LINKING_TABLES >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_ZIP_CODE_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.LOAD_MEDICAL_SCHOOL_TABLE >> OneViewDAG.REFRESH_PHYSICIAN_VIEW
OneViewDAG.REFRESH_PHYSICIAN_VIEW >> OneViewDAG.REINDEX_PHYSICIAN_VIEW

OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.REINDEX_PROVIDER_VIEW
OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.fan_in('LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE', 'REFRESH_PROVIDER_VIEW')
OneViewDAG.fan_in('LOAD_BUSINESS_TABLE', 'REFRESH_PROVIDER_VIEW')
OneViewDAG.fan_in('LOAD_IQVIA_PROVIDER_TABLE', 'REFRESH_PROVIDER_VIEW')
OneViewDAG.LOAD_SPECIALTY_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_LINKING_TABLES >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_ZIP_CODE_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.LOAD_MEDICAL_SCHOOL_TABLE >> OneViewDAG.REFRESH_PROVIDER_VIEW
OneViewDAG.REFRESH_PROVIDER_VIEW >> OneViewDAG.REINDEX_PROVIDER_VIEW
