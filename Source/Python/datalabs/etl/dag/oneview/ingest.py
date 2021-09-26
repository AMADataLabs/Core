''' DAG definition for the DAG Scheduler. '''
from   datalabs.etl.dag.dag import DAG
from   datalabs.etl.jdbc.extract import JDBCExtractorTask
from   datalabs.etl.http.extract import HTTPFileExtractorTask
from   datalabs.etl.sftp.extract import SFTPFileExtractorTask, SFTPIBM437TextFileExtractorTask
from   datalabs.etl.oneview.melissa.transform import MelissaTransformerTask
from   datalabs.etl.oneview.ppd.transform import PPDTransformerTask, NPITransformerTask, PhysicianTransformerTask
from   datalabs.etl.oneview.reference.transform import TypeOfPracticeTransformerTask, PresentEmploymentTransformerTask,\
    CoreBasedStatisticalAreaTransformerTask, FederalInformationProcessingStandardCountyTransformerTask, \
    MajorProfessionalActivityTransformerTask, SpecialtyMergeTransformerTask, \
    StaticReferenceTablesTransformerTask, ClassOfTradeTransformerTask, StateTransformerTask, \
    MedicalSchoolTransformerTask
from   datalabs.etl.oneview.residency.transform import ResidencyTransformerTask
from   datalabs.etl.oneview.iqvia.transform import IQVIATransformerTask, IQVIAUpdateTransformerTask
from   datalabs.etl.oneview.credentialing.transform import CredentialingTransformerTask, \
    CredentialingFinalTransformerTask
from   datalabs.etl.oneview.link.transform import CredentialingCustomerInstitutionTransformerTask, \
    CredentialingCustomerBusinessTransformerTask, ResidencyProgramPhysicianTransformerTask
from   datalabs.etl.oneview.historical_resident.transform import HistoricalResidentTransformerTask
from   datalabs.etl.orm.load import ORMLoaderTask


class OneViewDAG(DAG):
    EXTRACT_PPD: SFTPIBM437TextFileExtractorTask
    EXTRACT_PARTY_KEYS: JDBCExtractorTask
    SUPPLEMENT_PPD_TABLE: PPDTransformerTask
    CREATE_PHYSICIAN_NPI_TABLE: NPITransformerTask
    CREATE_PHYSICIAN_TABLE: PhysicianTransformerTask
    LOAD_PHYSICIAN_TABLE: ORMLoaderTask
    EXTRACT_MELISSA: JDBCExtractorTask
    CREATE_MELISSA_TABLES: MelissaTransformerTask
    LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE: ORMLoaderTask
    LOAD_COUNTY_TABLE: ORMLoaderTask
    LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE: ORMLoaderTask
    LOAD_ZIP_CODE_TABLE: ORMLoaderTask
    LOAD_AREA_CODE_TABLE: ORMLoaderTask
    LOAD_CENSUS_TABLE: ORMLoaderTask
    LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE: ORMLoaderTask
    EXTRACT_TYPE_OF_PRACTICE: JDBCExtractorTask
    CREATE_TYPE_OF_PRACTICE_TABLE: TypeOfPracticeTransformerTask
    EXTRACT_PRESENT_EMPLOYMENT: JDBCExtractorTask
    CREATE_PRESENT_EMPLOYMENT_TABLE: PresentEmploymentTransformerTask
    EXTRACT_CORE_BASED_STATISTICAL_AREA: HTTPFileExtractorTask
    CREATE_CORE_BASED_STATISTICAL_AREA_TABLE: CoreBasedStatisticalAreaTransformerTask
    EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY: HTTPFileExtractorTask
    CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: \
        FederalInformationProcessingStandardCountyTransformerTask
    EXTRACT_SPECIALTY: JDBCExtractorTask
    REMOVE_UNUSED_SPECIALTIES: SpecialtyMergeTransformerTask
    EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY: JDBCExtractorTask
    CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: MajorProfessionalActivityTransformerTask
    LOAD_TYPE_OF_PRACTICE_TABLE: ORMLoaderTask
    LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: ORMLoaderTask
    LOAD_SPECIALTY_TABLE: ORMLoaderTask
    LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: ORMLoaderTask
    LOAD_CORE_BASED_STATISTICAL_AREA_TABLE: ORMLoaderTask
    LOAD_PRESENT_EMPLOYMENT_TABLE: ORMLoaderTask
    LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: ORMLoaderTask
    EXTRACT_RESIDENCY: SFTPFileExtractorTask
    CREATE_RESIDENCY_TABLES: ResidencyTransformerTask
    LOAD_RESIDENCY_INSTITUTION_TABLE: ORMLoaderTask
    LOAD_RESIDENCY_PROGRAM_TABLE: ORMLoaderTask
    LOAD_RESIDENCY_PERSONNEL_TABLE: ORMLoaderTask
    EXTRACT_IQVIA_BUSINESS: JDBCExtractorTask
    EXTRACT_IQVIA_PROVIDER: JDBCExtractorTask
    EXTRACT_IQVIA_PROVIDER_AFFILIATION: JDBCExtractorTask
    CREATE_IQVIA_UPDATE_TABLE: IQVIAUpdateTransformerTask
    CREATE_BUSINESS_AND_PROVIDER_TABLES: IQVIATransformerTask
    LOAD_IQVIA_BUSINESS_PROVIDER_TABLES: ORMLoaderTask
    LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE: ORMLoaderTask
    LOAD_IQVIA_UPDATE_TABLE: ORMLoaderTask
    EXTRACT_CREDENTIALING: SFTPFileExtractorTask
    EXTRACT_CREDENTIALING_ADDRESSES: SFTPFileExtractorTask
    CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES: CredentialingTransformerTask
    LOAD_CREDENTIALING_CUSTOMER_PRODUCT_TABLES: ORMLoaderTask
    LOAD_CREDENTIALING_ORDER_TABLE: ORMLoaderTask
    MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE: CredentialingFinalTransformerTask
    EXTRACT_PHYSICIAN_RACE_ETHNICITY: SFTPFileExtractorTask
    EXTRACT_HISTORICAL_RESIDENT: SFTPFileExtractorTask
    CREATE_HISTORICAL_RESIDENT_TABLE: HistoricalResidentTransformerTask
    LOAD_HISTORICAL_RESIDENT_TABLE: ORMLoaderTask
    EXTRACT_MEDICAL_STUDENT: SFTPFileExtractorTask
    CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE: CredentialingCustomerInstitutionTransformerTask
    CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE: CredentialingCustomerBusinessTransformerTask
    CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE: ResidencyProgramPhysicianTransformerTask
    LOAD_LINKING_TABLES: ORMLoaderTask
    EXTRACT_STATE_TABLE: JDBCExtractorTask
    EXTRACT_CLASS_OF_TRADE_TABLE: JDBCExtractorTask
    CREATE_STATIC_REFERENCE_TABLE: StaticReferenceTablesTransformerTask
    CREATE_STATE_TABLE: StateTransformerTask
    CREATE_CLASS_OF_TRADE_TABLE: ClassOfTradeTransformerTask
    LOAD_CLASS_OF_TRADE_TABLE: ORMLoaderTask
    LOAD_STATE_TABLE: ORMLoaderTask
    LOAD_STATIC_REFERENCE_TABLE: ORMLoaderTask
    EXTRACT_MEDICAL_SCHOOL_REFERENCE_TABLE: JDBCExtractorTask
    CREATE_MEDICAL_SCHOOL_REFERENCE_TABLE: MedicalSchoolTransformerTask
    LOAD_MEDICAL_SCHOOL_REFERENCE_TABLE: ORMLoaderTask


# pylint: disable=pointless-statement
OneViewDAG.EXTRACT_MELISSA >> OneViewDAG.CREATE_MELISSA_TABLES
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_AREA_CODE_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_CENSUS_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_METROPOLITAN_STATISTICAL_AREA_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_MELISSA_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_COUNTY_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_ZIP_CODE_CORE_BASED_STATISTICAL_AREA_TABLE
OneViewDAG.CREATE_MELISSA_TABLES >> OneViewDAG.LOAD_ZIP_CODE_TABLE

OneViewDAG.EXTRACT_PPD >> OneViewDAG.SUPPLEMENT_PPD_TABLE
OneViewDAG.EXTRACT_PHYSICIAN_RACE_ETHNICITY >> OneViewDAG.SUPPLEMENT_PPD_TABLE
OneViewDAG.EXTRACT_MEDICAL_STUDENT >> OneViewDAG.SUPPLEMENT_PPD_TABLE
OneViewDAG.EXTRACT_PARTY_KEYS >> OneViewDAG.CREATE_PHYSICIAN_NPI_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE
OneViewDAG.SUPPLEMENT_PPD_TABLE >> OneViewDAG.CREATE_PHYSICIAN_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE

OneViewDAG.LOAD_STATE_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_SPECIALTY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE
OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE >> OneViewDAG.LOAD_PHYSICIAN_TABLE


OneViewDAG.CREATE_PHYSICIAN_TABLE >> OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE \
    >> OneViewDAG.LOAD_LINKING_TABLES
OneViewDAG.LOAD_RESIDENCY_PERSONNEL_TABLE >> OneViewDAG.LOAD_LINKING_TABLES
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.LOAD_LINKING_TABLES

OneViewDAG.EXTRACT_TYPE_OF_PRACTICE \
    >> OneViewDAG.CREATE_TYPE_OF_PRACTICE_TABLE \
    >> OneViewDAG.LOAD_TYPE_OF_PRACTICE_TABLE

OneViewDAG.EXTRACT_PRESENT_EMPLOYMENT \
    >> OneViewDAG.CREATE_PRESENT_EMPLOYMENT_TABLE \
    >> OneViewDAG.LOAD_PRESENT_EMPLOYMENT_TABLE

OneViewDAG.EXTRACT_CORE_BASED_STATISTICAL_AREA \
    >> OneViewDAG.CREATE_CORE_BASED_STATISTICAL_AREA_TABLE \
    >> OneViewDAG.LOAD_CORE_BASED_STATISTICAL_AREA_TABLE

OneViewDAG.EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY \
    >> OneViewDAG.CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE \
    >> OneViewDAG.LOAD_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE

OneViewDAG.EXTRACT_SPECIALTY >> OneViewDAG.CREATE_PHYSICIAN_TABLE >> OneViewDAG.REMOVE_UNUSED_SPECIALTIES \
    >> OneViewDAG.LOAD_SPECIALTY_TABLE
OneViewDAG.EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY >> OneViewDAG.CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE \
    >> OneViewDAG.LOAD_MAJOR_PROFESSIONAL_ACTIVITY_TABLE

OneViewDAG.EXTRACT_RESIDENCY  >> OneViewDAG.CREATE_RESIDENCY_TABLES \
    >> OneViewDAG.LOAD_RESIDENCY_INSTITUTION_TABLE \
    >> OneViewDAG.LOAD_RESIDENCY_PROGRAM_TABLE \
    >> OneViewDAG.LOAD_RESIDENCY_PERSONNEL_TABLE

OneViewDAG.EXTRACT_IQVIA_BUSINESS >> OneViewDAG.CREATE_BUSINESS_AND_PROVIDER_TABLES
OneViewDAG.EXTRACT_IQVIA_PROVIDER >> OneViewDAG.CREATE_BUSINESS_AND_PROVIDER_TABLES
OneViewDAG.EXTRACT_IQVIA_PROVIDER_AFFILIATION >> OneViewDAG.CREATE_BUSINESS_AND_PROVIDER_TABLES \
    >> OneViewDAG.LOAD_IQVIA_BUSINESS_PROVIDER_TABLES \
OneViewDAG.EXTRACT_IQVIA_BUSINESS >> OneViewDAG.CREATE_IQVIA_UPDATE_TABLE \
    >> OneViewDAG.LOAD_IQVIA_UPDATE_TABLE

OneViewDAG.LOAD_IQVIA_BUSINESS_PROVIDER_TABLES >> OneViewDAG.LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE
OneViewDAG.LOAD_IQVIA_UPDATE_TABLE >> OneViewDAG.LOAD_IQVIA_PROVIDER_AFFILIATION_TABLE
OneViewDAG.LOAD_IQVIA_UPDATE_TABLE >> OneViewDAG.LOAD_IQVIA_BUSINESS_PROVIDER_TABLES
OneViewDAG.LOAD_STATIC_REFERENCE_TABLE >> OneViewDAG.LOAD_IQVIA_BUSINESS_PROVIDER_TABLES
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.LOAD_IQVIA_BUSINESS_PROVIDER_TABLES

OneViewDAG.EXTRACT_CREDENTIALING >> OneViewDAG.EXTRACT_CREDENTIALING_ADDRESSES \
    >> OneViewDAG.MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE \
    >> OneViewDAG.LOAD_CREDENTIALING_CUSTOMER_PRODUCT_TABLES \
    >> OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE

OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.LOAD_CREDENTIALING_ORDER_TABLE

OneViewDAG.CREATE_PHYSICIAN_TABLE >> OneViewDAG.CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE \
    >> OneViewDAG.LOAD_LINKING_TABLES

OneViewDAG.EXTRACT_HISTORICAL_RESIDENT \
    >> OneViewDAG.CREATE_HISTORICAL_RESIDENT_TABLE \
    >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE
OneViewDAG.LOAD_PHYSICIAN_TABLE >> OneViewDAG.LOAD_HISTORICAL_RESIDENT_TABLE

OneViewDAG.CREATE_STATIC_REFERENCE_TABLE >> OneViewDAG.LOAD_STATIC_REFERENCE_TABLE

OneViewDAG.EXTRACT_STATE_TABLE >> OneViewDAG.CREATE_STATE_TABLE >> OneViewDAG.LOAD_STATE_TABLE

OneViewDAG.EXTRACT_CLASS_OF_TRADE_TABLE >> OneViewDAG.CREATE_CLASS_OF_TRADE_TABLE \
    >> OneViewDAG.LOAD_CLASS_OF_TRADE_TABLE

OneViewDAG.EXTRACT_MEDICAL_SCHOOL_REFERENCE_TABLE >> OneViewDAG.CREATE_MEDICAL_SCHOOL_REFERENCE_TABLE \
    >> OneViewDAG.LOAD_MEDICAL_SCHOOL_REFERENCE_TABLE
