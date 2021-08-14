''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.models import Variable
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago


### Configuration Bootstraping ###
DAG_ID = 'oneview'
DEPLOYMENT_ID = Variable.get('DEPLOYMENT_ID')
IMAGE = Variable.get(f'{DAG_ID.upper()}_IMAGE')

BASE_ENVIRONMENT = dict(
    TASK_WRAPPER_CLASS='datalabs.etl.dag.task.DAGTaskWrapper',
    ETCD_HOST=Variable.get('ETCD_HOST'),
    ETCD_USERNAME=DAG_ID,
    ETCD_PASSWORD=Variable.get(f'{DAG_ID.upper()}_ETCD_PASSWORD'),
    ETCD_PREFIX=f'{DAG_ID.upper()}_'
)

### DAG definition ###
ONEVIEW_ETL_DAG = DAG(
    dag_id=DAG_ID,
    default_args=dict(
        owner='airflow',
        resources=dict(
            limit_memory="8G",
            limit_cpu="2"
        ),
        is_delete_operator_pod=True,
        namespace=f'hsg-data-labs-{DEPLOYMENT_ID}',
        image=IMAGE,
        do_xcom_push=False,
        in_cluster=True,
        get_logs=True,
    ),
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['OneView'],
)


with ONEVIEW_ETL_DAG:
    EXTRACT_PPD = KubernetesPodOperator(
        name="extract_ppd",
        task_id="extract_ppd",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_TYPE_OF_PRACTICE = KubernetesPodOperator(
        name="extract_type_of_practice",
        task_id="extract_type_of_practice",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_PRESENT_EMPLOYMENT = KubernetesPodOperator(
        name="extract_present_employment",
        task_id="extract_present_employment",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY = KubernetesPodOperator(
        name="extract_major_professional_activity",
        task_id="extract_major_professional_activity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_CORE_BASED_STATISTICAL_AREA = KubernetesPodOperator(
        name="extract_core_based_statistical_area",
        task_id="extract_core_based_statistical_area",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.http.extract.HTTPFileExtractorTask')},
    )

    EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY = KubernetesPodOperator(
        name="extract_federal_information_processing_standard_county",
        task_id="extract_federal_information_processing_standard_county",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.http.extract.HTTPFileExtractorTask')},
    )

    EXTRACT_SPECIALTY = KubernetesPodOperator(
        name="extract_specialty",
        task_id="extract_specialty",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_RESIDENCY = KubernetesPodOperator(
        name="extract_residency",
        task_id="extract_residency",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

    EXTRACT_IQVIA = KubernetesPodOperator(
        name="extract_iqvia",
        task_id="extract_iqvia",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    EXTRACT_CREDENTIALING = KubernetesPodOperator(
        name="extract_credentialing",
        task_id="extract_credentialing",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    EXTRACT_CREDENTIALING_ADDRESSES = KubernetesPodOperator(
        name="extract_credentialing_addresses",
        task_id="extract_credentialing_addresses",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

    EXTRACT_PHYSICIAN_RACE_ETHNICITY = KubernetesPodOperator(
        name="extract_physician_race_ethnicity",
        task_id="extract_physician_race_ethnicity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
    )

    EXTRACT_MELISSA = KubernetesPodOperator(
        name="extract_melissa",
        task_id="extract_melissa",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
    )

    EXTRACT_PHYSICIAN_NATIONAL_PROVIDER_IDENTIFIERS = KubernetesPodOperator(
        name="extract_physician_national_provider_identifiers",
        task_id="extract_physician_national_provider_identifiers",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    EXTRACT_HISTORICAL_RESIDENCY = KubernetesPodOperator(
        name="extract_historical_residency",
        task_id="extract_historical_residency",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    CREATE_PHYSICIAN_TABLE = KubernetesPodOperator(
        name="create_physician_table",
        task_id="create_physician_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.oneview.ppd.transform.PPDTransformerTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    CREATE_TYPE_OF_PRACTICE_TABLE = KubernetesPodOperator(
        name="create_type_of_practice_table",
        task_id="create_type_of_practice_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.TypeOfPracticeTransformerTask')
        },
    )

    CREATE_PRESENT_EMPLOYMENT_TABLE = KubernetesPodOperator(
        name="create_present_employment_table",
        task_id="create_present_employment_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.PresentEmploymentTransformerTask')
        },
    )

    CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE = KubernetesPodOperator(
        name="create_major_professional_activity_table",
        task_id="create_major_professional_activity_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.MajorProfessionalActivityTransformerTask')
        },
    )

    CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE = KubernetesPodOperator(
        name="create_federal_information_processing_standard_county_table",
        task_id="create_federal_information_processing_standard_county_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(
                TASK_CLASS='datalabs.etl.oneview.reference.transform.'
                           'FederalInformationProcessingStandardCountyTransformerTask'
            )
        },
    )

    CREATE_CORE_BASED_STATISTICAL_AREA_TABLE = KubernetesPodOperator(
        name="create_core_based_statistical_area_table",
        task_id="create_core_based_statistical_area_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.CoreBasedStatisticalAreaTransformerTask')
        },
    )

    REMOVE_UNUSED_SPECIALTIES = KubernetesPodOperator(
        name="remove_unused_specialties",
        task_id="remove_unused_specialties",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.SpecialtyMergeTransformerTask')
        },
    )

    CREATE_RESIDENCY_PROGRAM_TABLES = KubernetesPodOperator(
        name="create_residency_program_tables",
        task_id="create_residency_program_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.residency.transform.ResidencyTransformerTask')
        },
    )

    CREATE_BUSINESS_AND_PROVIDER_TABLES = KubernetesPodOperator(
        name="create_business_and_provider_tables",
        task_id="create_business_and_provider_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.oneview.iqvia.transform.IQVIATransformerTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES = KubernetesPodOperator(
        name="create_credentialing_customer_product_and_order_tables",
        task_id="create_credentialing_customer_product_and_order_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingTransformerTask')
        },
    )

    MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE = KubernetesPodOperator(
        name="merge_credentialing_addresses_into_customer_table",
        task_id="merge_credentialing_addresses_into_customer_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingFinalTransformerTask')
        },
    )

    CREATE_MELISSA_TABLES = KubernetesPodOperator(
        name="create_melissa_tables",
        task_id="create_melissa_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.melissa.transform.MelissaTransformerTask')
        },
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    # CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE = KubernetesPodOperator(
    #     name="create_credentialing_customer_institution_table",
    #     task_id="create_credentialing_customer_institution_table",
    #     cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
    #     env_vars={
    #         **BASE_ENVIRONMENT,
    #         **dict(TASK_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerInstitutionTransformerTask')
    #     },
    # )
    #
    # CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE = KubernetesPodOperator(
    #     name="create_credentialing_customer_business_table",
    #     task_id="create_credentialing_customer_business_table",
    #     cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
    #     env_vars={
    #        **BASE_ENVIRONMENT,
    #        **dict(TASK_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerBusinessTransformerTask')
    #     },
    # )

    CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE = KubernetesPodOperator(
        name="create_residency_program_physician_table",
        task_id="create_residency_program_physician_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
           **BASE_ENVIRONMENT,
           **dict(TASK_CLASS='datalabs.etl.oneview.link.transform.ResidencyProgramPhysicianTransformerTask')
        },
    )

    CREATE_IQVIA_UPDATE_TABLE = KubernetesPodOperator(
        name="create_iqvia_update_table",
        task_id="create_iqvia_update_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.iqvia.transform.IQVIAUpdateTransformerTask')
        },
    )

    # LOAD_PHYSICIAN_TABLE_INTO_DATABASE = KubernetesPodOperator(
    #     name="load_physician_table_into_database",
    #     task_id="load_physician_table_into_database",
    #     cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
    #     env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
    # )

    CREATE_HISTORICAL_RESIDENCY_TABLE = KubernetesPodOperator(
        name="create_historical_residency_table",
        task_id="create_historical_residency_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={
            **BASE_ENVIRONMENT,
            **dict(TASK_CLASS='datalabs.etl.oneview.historical_residency.transform.HistoricalResidencyTransformerTask')
        },
    )
    LOAD_REFERENCE_TABLES_INTO_DATABASE = KubernetesPodOperator(
        name="load_reference_tables_into_database",
        task_id="load_reference_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
        is_delete_operator_pod=(DEPLOYMENT_ID == 'prod'),
    )

    LOAD_RESIDENCY_TABLES_INTO_DATABASE = KubernetesPodOperator(
        name="load_residency_tables_into_database",
        task_id="load_residency_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
    )

    LOAD_IQVIA_TABLES_INTO_DATABASE = KubernetesPodOperator(
        name="load_iqvia_tables_into_database",
        task_id="load_iqvia_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
    )

    LOAD_CREDENTIALING_TABLES_INTO_DATABASE = KubernetesPodOperator(
        name="load_credentialing_tables_into_database",
        task_id="load_credentialing_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
    )

    LOAD_MELISSA_TABLES_INTO_DATABASE = KubernetesPodOperator(
        name="load_melissa_tables_into_database",
        task_id="load_melissa_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
    )

    # LOAD_LINKING_TABLES_INTO_DATABASE = KubernetesPodOperator(
    #     name="load_linking_tables_into_database",
    #     task_id="load_linking_tables_into_database",
    #     cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
    #     env_vars={**BASE_ENVIRONMENT, **dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask')},
    # )

    MIGRATE_DATABASE = KubernetesPodOperator(
        name="migrate_database",
        task_id="migrate_database",
        cmds=['./upgrade-database'],
        env_vars=BASE_ENVIRONMENT,
    )

# pylint: disable=pointless-statement
MIGRATE_DATABASE
EXTRACT_PPD >> CREATE_PHYSICIAN_TABLE
EXTRACT_PHYSICIAN_NATIONAL_PROVIDER_IDENTIFIERS >> CREATE_PHYSICIAN_TABLE
CREATE_PHYSICIAN_TABLE # >> LOAD_PHYSICIAN_TABLE_INTO_DATABASE
EXTRACT_TYPE_OF_PRACTICE >> CREATE_TYPE_OF_PRACTICE_TABLE >> LOAD_REFERENCE_TABLES_INTO_DATABASE
EXTRACT_PRESENT_EMPLOYMENT >> CREATE_PRESENT_EMPLOYMENT_TABLE >> LOAD_REFERENCE_TABLES_INTO_DATABASE
EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY >> CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> LOAD_REFERENCE_TABLES_INTO_DATABASE
EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY >> CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE
CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE >> LOAD_REFERENCE_TABLES_INTO_DATABASE
EXTRACT_CORE_BASED_STATISTICAL_AREA >> CREATE_CORE_BASED_STATISTICAL_AREA_TABLE >> LOAD_REFERENCE_TABLES_INTO_DATABASE
EXTRACT_SPECIALTY >> REMOVE_UNUSED_SPECIALTIES
CREATE_PHYSICIAN_TABLE >> REMOVE_UNUSED_SPECIALTIES
REMOVE_UNUSED_SPECIALTIES >> LOAD_REFERENCE_TABLES_INTO_DATABASE
EXTRACT_RESIDENCY >> CREATE_RESIDENCY_PROGRAM_TABLES >> LOAD_RESIDENCY_TABLES_INTO_DATABASE
EXTRACT_IQVIA >> CREATE_BUSINESS_AND_PROVIDER_TABLES >> LOAD_IQVIA_TABLES_INTO_DATABASE
EXTRACT_IQVIA >> CREATE_IQVIA_UPDATE_TABLE
EXTRACT_CREDENTIALING >> CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES
EXTRACT_CREDENTIALING_ADDRESSES >> MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE
EXTRACT_HISTORICAL_RESIDENCY >> CREATE_HISTORICAL_RESIDENCY_TABLE
CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES >> MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE
MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> LOAD_CREDENTIALING_TABLES_INTO_DATABASE
EXTRACT_PHYSICIAN_RACE_ETHNICITY >> CREATE_PHYSICIAN_TABLE
CREATE_RESIDENCY_PROGRAM_TABLES >> CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE
CREATE_PHYSICIAN_TABLE >> CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE
# CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE >> LOAD_LINKING_TABLES_INTO_DATABASE
EXTRACT_MELISSA >> CREATE_MELISSA_TABLES >> LOAD_MELISSA_TABLES_INTO_DATABASE
