""" OneView ETL DAG definition. """
from   collections import namedtuple

import paradag

from   datalabs.etl.dag import DAG

class DAG(paradag.DAG):
    TASK_CLASSES = dict()

    def __init__(self):
        self._generate()

    def _generate(self):
        pass

class TaskVertex(object):
    def __init__(self, task_class):
        self._task_class = task_class

class OneViewDAG(DAG):
    EXTRACT_PPD: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_TYPE_OF_PRACTICE: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_PRESENT_EMPLOYMENT: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_CORE_BASED_STATISTICAL_AREA: 'datalabs.etl.http.extract.HTTPFileExtractorTask'
    EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY='datalabs.etl.http.extract.HTTPFileExtractorTask'
    EXTRACT_SPECIALTY: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_RESIDENCY: 'datalabs.etl.sftp.extract.SFTPFileExtractorTask'
    EXTRACT_IQVIA: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_CREDENTIALING_MAIN: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_CREDENTIALING_ADDRESSES: 'datalabs.etl.sftp.extract.SFTPFileExtractorTask'
    EXTRACT_PHYSICIAN_RACE_ETHNICITY: 'datalabs.etl.sftp.extract.SFTPFileExtractorTask'
    EXTRACT_MELISSA: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    EXTRACT_PHYSICIAN_NATIONAL_PROVIDER_IDENTIFIERS: 'datalabs.etl.jdbc.extract.JDBCExtractorTask'
    CREATE_PHYSICIAN_TABLE: 'datalabs.etl.oneview.ppd.transform.PPDTransformerTask'
    CREATE_TYPE_OF_PRACTICE_TABLE: 'datalabs.etl.oneview.reference.transform.TypeOfPracticeTransformerTask'
    CREATE_PRESENT_EMPLOYMENT_TABLE: 'datalabs.etl.oneview.reference.transform.PresentEmploymentTransformerTask'
    CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE:\
        'datalabs.etl.oneview.reference.transform.MajorProfessionalActivityTransformerTask'
    CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE:\
        'datalabs.etl.oneview.reference.transform.FederalInformationProcessingStandardCountyTransformerTask'
    CREATE_CORE_BASED_STATISTICAL_AREA_TABLE:\
        'datalabs.etl.oneview.reference.transform.CoreBasedStatisticalAreaTransformerTask'
    REMOVE_UNUSED_SPECIALTIES: 'datalabs.etl.oneview.reference.transform.SpecialtyMergeTransformerTask'
    CREATE_RESIDENCY_PROGRAM_TABLES: 'datalabs.etl.oneview.residency.transform.ResidencyTransformerTask'
    CREATE_BUSINESS_AND_PROVIDER_TABLES: 'datalabs.etl.oneview.iqvia.transform.IQVIATransformerTask'
    CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES:\
        'datalabs.etl.oneview.credentialing.transform.CredentialingTransformerTask'
    MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE:\
        'datalabs.etl.oneview.credentialing.transform.CredentialingFinalTransformerTask'
    CREATE_PHYSICIAN_RACE_ETHNICITY_TABLE:\
        'datalabs.etl.oneview.race_ethnicity.transform.RaceEthnicityTransformerTask',
    CREATE_MELISSA_TABLES: 'datalabs.etl.oneview.melissa.transform.MelissaTransformerTask'
    CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE:\
        'datalabs.etl.oneview.link.transform.CredentialingCustomerInstitutionTransformerTask'
    CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE:\
        'datalabs.etl.oneview.link.transform.CredentialingCustomerBusinessTransformerTask'
    CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE:\
        'datalabs.etl.oneview.link.transform.ResidencyProgramPhysicianTransformerTask'
    LOAD_PHYSICIAN_TABLE_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_REFERENCE_TABLES_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_RESIDENCY_TABLES_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_IQVIA_TABLES_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_RACE_ETHNICITY_TABLE_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_CREDENTIALING_TABLES_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_MELISSA_TABLES_INTO_DATABASE: 'datalabs.etl.orm.load.ORMLoaderTask'
    LOAD_LINKING_TABLES_INTO_DATABASE='datalabs.etl.orm.load.ORMLoaderTask'

    EDGES = dict(
        EXTRACT_PPD: 'CREATE_PHYSICIAN_TABLE'
        EXTRACT_PHYSICIAN_NATIONAL_PROVIDER_IDENTIFIERS: 'CREATE_PHYSICIAN_TABLE'
        CREATE_PHYSICIAN_TABLE=[
            'LOAD_PHYSICIAN_TABLE_INTO_DATABASE',
            'REMOVE_UNUSED_SPECIALTIES'
        ]
        EXTRACT_TYPE_OF_PRACTICE: 'CREATE_TYPE_OF_PRACTICE_TABLE'
        CREATE_TYPE_OF_PRACTICE_TABLE: 'LOAD_REFERENCE_TABLES_INTO_DATABASE'
        EXTRACT_PRESENT_EMPLOYMENT: 'CREATE_PRESENT_EMPLOYMENT_TABLE'
        CREATE_PRESENT_EMPLOYMENT_TABLE: 'LOAD_REFERENCE_TABLES_INTO_DATABASE'
        EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY: 'CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE'
        CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE: 'LOAD_REFERENCE_TABLES_INTO_DATABASE'
        EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY=[
            'CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE'
        ]
        CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE: 'LOAD_REFERENCE_TABLES_INTO_DATABASE'
        EXTRACT_CORE_BASED_STATISTICAL_AREA: 'CREATE_CORE_BASED_STATISTICAL_AREA_TABLE'
        CREATE_CORE_BASED_STATISTICAL_AREA_TABLE: 'LOAD_REFERENCE_TABLES_INTO_DATABASE'
        EXTRACT_SPECIALTY: 'REMOVE_UNUSED_SPECIALTIES'
        REMOVE_UNUSED_SPECIALTIES: 'LOAD_REFERENCE_TABLES_INTO_DATABASE'
        EXTRACT_RESIDENCY: 'CREATE_RESIDENCY_PROGRAM_TABLES'
        CREATE_RESIDENCY_PROGRAM_TABLES=[
            'LOAD_RESIDENCY_TABLES_INTO_DATABASE',
            'CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE',
            'CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE'
        ],
        EXTRACT_IQVIA: 'CREATE_BUSINESS_AND_PROVIDER_TABLES'
        CREATE_BUSINESS_AND_PROVIDER_TABLES=[
            'LOAD_IQVIA_TABLES_INTO_DATABASE',
            'CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE'
        ],
        EXTRACT_CREDENTIALING_MAIN: 'CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES'
        EXTRACT_CREDENTIALING_ADDRESSES: 'MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE'
        CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES: 'MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE'
        MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE=[
            'LOAD_CREDENTIALING_TABLES_INTO_DATABASE',
            'CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE',
            'CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE'
        ],
        EXTRACT_PHYSICIAN_RACE_ETHNICITY: 'CREATE_PHYSICIAN_RACE_ETHNICITY_TABLE'
        CREATE_PHYSICIAN_RACE_ETHNICITY_TABLE: 'LOAD_RACE_ETHNICITY_TABLE_INTO_DATABASE'
        CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE: 'LOAD_LINKING_TABLES_INTO_DATABASE'
        CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE: 'LOAD_LINKING_TABLES_INTO_DATABASE'
        CREATE_PHYSICIAN_TABLE: 'CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE'
        CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE: 'LOAD_LINKING_TABLES_INTO_DATABASE'
        EXTRACT_MELISSA: 'CREATE_MELISSA_TABLES'
        CREATE_MELISSA_TABLES: 'LOAD_MELISSA_TABLES_INTO_DATABASE'
    )
