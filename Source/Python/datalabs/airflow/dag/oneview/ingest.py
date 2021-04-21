''' Masterfile OneView DAG definition. '''
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


ETL_CONFIG = k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-etl'))
MINIO_SECRET = Secret('env', None, 'oneview-etl-minio')
AIMS_SECRET = Secret('env', None, 'oneview-etl-aims')
ODS_SECRET = Secret('env', None, 'oneview-etl-ods')
SFTP_SECRET = Secret('env', None, 'oneview-etl-sftp')
DATABASE_SECRET = Secret('env', None, 'oneview-etl-database')
DOCKER_IMAGE = 'docker-registry.default.svc:5000/hsg-data-labs-dev/oneview-etl:1.2.4'

ONEVIEW_ETL_DAG = DAG(
    dag_id='oneview',
    default_args={'owner': 'airflow'},
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['OneView'],
)


with ONEVIEW_ETL_DAG:
    EXTRACT_PPD = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_ppd",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_ppd",
        get_logs=True,
    )

    EXTRACT_TYPE_OF_PRACTICE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_type_of_practice",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_type_of_practice",
        get_logs=True,
    )

    EXTRACT_PRESENT_EMPLOYMENT = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_present_employment",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_present_employment",
        get_logs=True,
    )

    EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_major_professional_activity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_major_professional_activity",
        get_logs=True,
    )

    EXTRACT_CORE_BASED_STATISTICAL_AREA = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_core_based_statistical_area",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.http.extract.HTTPFileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_core_based_statistical_area",
        get_logs=True,
    )

    EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_federal_information_processing_standard_county",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.http.extract.HTTPFileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_federal_information_processing_standard_county",
        get_logs=True,
    )

    EXTRACT_SPECIALTY = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_specialty",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_specialty",
        get_logs=True,
    )

    EXTRACT_RESIDENCY = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_residency",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[SFTP_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_residency",
        get_logs=True,
    )

    EXTRACT_IQVIA = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_iqvia",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_iqvia",
        get_logs=True,
    )

    EXTRACT_CREDENTIALING_MAIN = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_credentialing",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[ODS_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="extract_credentialing",
        get_logs=True,
    )

    EXTRACT_CREDENTIALING_ADDRESSES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_credentialing_addresses",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[SFTP_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_credentialing_addresses",
        get_logs=True,
    )

    EXTRACT_PHYSICIAN_RACE_ETHNICITY = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="extract_physician_race_ethnicity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[SFTP_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_physician_race_ethnicity",
        get_logs=True,
    )

    CREATE_PHYSICIAN_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_physician_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.ppd.transform.PPDTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="create_physician_table",
        get_logs=True,
    )

    CREATE_TYPE_OF_PRACTICE_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        name="create_type_of_practice_table",
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.TypeOfPracticeTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="create_type_of_practice_table",
        get_logs=True,
    )

    CREATE_PRESENT_EMPLOYMENT_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_present_employment_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.PresentEmploymentTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="create_present_employment_table",
        get_logs=True,
    )

    CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_major_professional_activity_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.MajorProfessionalActivityTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="create_major_professional_activity_table",
        get_logs=True,
    )

    CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_federal_information_processing_standard_county_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(
            TASK_CLASS='datalabs.etl.oneview.reference.transform.'
                       'FederalInformationProcessingStandardCountyTransformerTask'
        ),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_federal_information_processing_standard_county_table",
        get_logs=True,
    )

    CREATE_CORE_BASED_STATISTICAL_AREA_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_core_based_statistical_area_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.CoreBasedStatisticalAreaTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_core_based_statistical_area_table",
        get_logs=True,
    )

    REMOVE_UNUSED_SPECIALTIES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="remove_unused_specialties",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.SpecialtyMergeTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="remove_unused_specialties",
        get_logs=True,
    )

    CREATE_RESIDENCY_PROGRAM_TABLES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_residency_program_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.residency.transform.ResidencyTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="create_residency_program_tables",
        get_logs=True,
    )

    CREATE_BUSINESS_AND_PROVIDER_TABLES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_business_and_provider_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.iqvia.transform.IQVIATransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="create_business_and_provider_tables",
        get_logs=True,
    )

    CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_credentialing_customer_product_and_order_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_credentialing_customer_product_and_order_tables",
        get_logs=True,
    )

    MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="merge_credentialing_addresses_into_customer_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingFinalTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="merge_credentialing_addresses_into_customer_table",
        get_logs=True,
    )

    CREATE_PHYSICIAN_RACE_ETHNICITY_TABLE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="create_physician_race_ethnicity_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.race_ethnicity.transform.RaceEthnicityTransformerTask'),
        do_xcom_push=False,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_physician_race_ethnicity_table",
        get_logs=True,
    )

#     CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE = KubernetesPodOperator(
#         namespace='hsg-data-labs-dev',
#         image=DOCKER_IMAGE,
#         name="create_credentialing_customer_institution_table",
#         cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
#         env_from=[ETL_CONFIG],
#         secrets=[MINIO_SECRET],
        # env_vars=dict(
        #     TASK_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerInstitutionTransformerTask'
        # ),
#         do_xcom_push=False,
#         is_delete_operator_pod=True,
#         in_cluster=True,
#         task_id="create_credentialing_customer_institution_table",
#         get_logs=True,
#     )
#
#     CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE = KubernetesPodOperator(
#         namespace='hsg-data-labs-dev',
#         image=DOCKER_IMAGE,
#         name="create_credentialing_customer_business_table",
#         cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
#         env_from=[ETL_CONFIG],
#         secrets=[MINIO_SECRET],
#         env_vars=dict(TASK_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerBusinessTransformerTask'),
#         do_xcom_push=False,
#         is_delete_operator_pod=True,
#         in_cluster=True,
#         task_id="create_credentialing_customer_business_table",
#         get_logs=True,
#     )
#
#     CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE = KubernetesPodOperator(
#         namespace='hsg-data-labs-dev',
#         image=DOCKER_IMAGE,
#         name="create_residency_program_physician_table",
#         cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
#         env_from=[ETL_CONFIG],
#         secrets=[MINIO_SECRET],
#         env_vars=dict(TASK_CLASS='datalabs.etl.oneview.link.transform.ResidencyProgramPhysicianTransformerTask'),
#         do_xcom_push=False,
#         is_delete_operator_pod=True,
#         in_cluster=True,
#         task_id="create_residency_program_physician_table",
#         get_logs=True,
#     )
#
    LOAD_TABLES_INTO_DATABASE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="load_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[ETL_CONFIG],
        secrets=[DATABASE_SECRET, MINIO_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask'),
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="load_tables_into_database",
        get_logs=True,
    )

    MIGRATE_DATABASE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="migrate_database",
        secrets=[DATABASE_SECRET],
        cmds=['./Deploy/OneView/upgrade-database'],
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="migrate_database",
        get_logs=True,
    )

    RESET_DATABASE = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image=DOCKER_IMAGE,
        name="reset_database",
        env_from=[ETL_CONFIG],
        secrets=[DATABASE_SECRET],
        env_vars=dict(TASK_CLASS='datalabs.etl.orm.load.ORMPreLoaderTask'),
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        do_xcom_push=False,
        is_delete_operator_pod=False,
        in_cluster=True,
        task_id="reset_database",
        get_logs=True,
    )

# # pylint: disable=pointless-statement
MIGRATE_DATABASE
RESET_DATABASE
EXTRACT_PPD >> CREATE_PHYSICIAN_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_TYPE_OF_PRACTICE >> CREATE_TYPE_OF_PRACTICE_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_PRESENT_EMPLOYMENT >> CREATE_PRESENT_EMPLOYMENT_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_MAJOR_PROFESSIONAL_ACTIVITY >> CREATE_MAJOR_PROFESSIONAL_ACTIVITY_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY >> CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE
CREATE_FEDERAL_INFORMATION_PROCESSING_STANDARD_COUNTY_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_CORE_BASED_STATISTICAL_AREA >> CREATE_CORE_BASED_STATISTICAL_AREA_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_SPECIALTY >> REMOVE_UNUSED_SPECIALTIES
CREATE_PHYSICIAN_TABLE >> REMOVE_UNUSED_SPECIALTIES
REMOVE_UNUSED_SPECIALTIES >> LOAD_TABLES_INTO_DATABASE
EXTRACT_RESIDENCY >> CREATE_RESIDENCY_PROGRAM_TABLES  # >> LOAD_TABLES_INTO_DATABASE
EXTRACT_IQVIA >> CREATE_BUSINESS_AND_PROVIDER_TABLES >> LOAD_TABLES_INTO_DATABASE
EXTRACT_CREDENTIALING_MAIN >> CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES
EXTRACT_CREDENTIALING_ADDRESSES >> MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE
CREATE_CREDENTIALING_CUSTOMER_PRODUCT_AND_ORDER_TABLES >> MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE
# MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> LOAD_TABLES_INTO_DATABASE
EXTRACT_PHYSICIAN_RACE_ETHNICITY >> CREATE_PHYSICIAN_RACE_ETHNICITY_TABLE >> LOAD_TABLES_INTO_DATABASE
# MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE
# CREATE_RESIDENCY_PROGRAM_TABLES >> CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE
# CREATE_CREDENTIALING_CUSTOMER_INSTITUTION_TABLE >> LOAD_TABLES_INTO_DATABASE
# MERGE_CREDENTIALING_ADDRESSES_INTO_CUSTOMER_TABLE >> CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE
# CREATE_BUSINESS_AND_PROVIDER_TABLES >> CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE
# CREATE_CREDENTIALING_CUSTOMER_BUSINESS_TABLE >> LOAD_TABLES_INTO_DATABASE
# CREATE_RESIDENCY_PROGRAM_TABLES >> CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE
# CREATE_PHYSICIAN_TABLE >> CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE
# CREATE_RESIDENCY_PROGRAM_PHYSICIAN_TABLE >> LOAD_TABLES_INTO_DATABASE
