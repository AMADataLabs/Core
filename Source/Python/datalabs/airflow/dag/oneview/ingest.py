from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


etl_config = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-etls'))
]
minio = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='minio-secret'))
]
aims = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='aims-secret'))
]
ods = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='ods-secret'))
]
sftp = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='sftp-secret'))
]
oneview_database = [
    k8s.V1EnvFromSource(secret_ref=k8s.V1ConfigMapEnvSource(name='final-database-secret'))
]

with DAG(
        dag_id='oneview-etl',
        default_args={'owner': 'airflow'},
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['OneView'],
) as dag:

    extract_ppd = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_ppd",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_ppd",
        get_logs=True,
    )

    create_physician_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_physician_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.ppd.transform.PPDTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_physician_table",
        get_logs=True,
    )

    extract_type_of_practice = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_type_of_practice",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_type_of_practice",
        get_logs=True,
    )

    create_type_of_practice_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        name="create_type_of_practice_table",
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_type_of_practice_table",
        get_logs=True,
    )

    extract_present_employment = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_present_employment",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_present_employment",
        get_logs=True,
    )

    create_present_employment_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name = "create_present_employment_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_present_employment_table",
        get_logs=True,
    )

    extract_major_professional_activity = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_major_professional_activity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_major_professional_activity",
        get_logs=True,
    )

    create_major_professional_activity_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_major_professional_activity_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_major_professional_activity_table",
        get_logs=True,
    )

    extract_federal_information_processing_standard_county = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_federal_information_processing_standard_county",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.http.extract.HTTPFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_federal_information_processing_standard_county",
        get_logs=True,
    )

    create_federal_information_processing_standard_county_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_federal_information_processing_standard_county_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.FederalInformationProcessingStandardCountyTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_federal_information_processing_standard_county_table",
        get_logs=True,
    )

    extract_core_based_statistical_area = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_core_based_statistical_area",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.http.extract.HTTPUnicodeTextFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_core_based_statistical_area",
        get_logs=True,
    )

    create_core_based_statistical_area_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_core_based_statistical_area_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_core_based_statistical_area_table",
        get_logs=True,
    )

    extract_specialty = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_specialty",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_specialty",
        get_logs=True,
    )

    create_specialty_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_specialty_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_specialty_table",
        get_logs=True,
    )

    remove_unused_specialties = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="remove_unused_specialties",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.reference.transform.SpecialtyMergeTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="remove_unused_specialties",
        get_logs=True,
    )

    extract_residency = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_residency",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, sftp],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPUnicodeTextFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_residency",
        get_logs=True,
    )

    create_residency_program_tables = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_residency_program_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_residency_program_tables",
        get_logs=True,
    )

    extract_iqvia = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_iqvia",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_iqvia",
        get_logs=True,
    )

    create_business_and_provider_tables = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_business_and_provider_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.iqvia.transform.IQVIATransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_business_and_provider_tables",
        get_logs=True,
    )

    extract_credentialing_main = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_credentialing",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_credentialing",
        get_logs=True,
    )

    create_credentialing_customer_product_and_order_tables = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_credentialing_customer_product_and_order_tables",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_credentialing_customer_product_and_order_tables",
        get_logs=True,
    )

    extract_credentialing_addresses = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_credentialing_addresses",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, sftp],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_credentialing_addresses",
        get_logs=True,
    )

    create_credentialing_addresses_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_credentialing_addresses_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.transform.PassThroughTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_credentialing_addresses_table",
        get_logs=True,
    )

    merge_credentialing_addresses_into_customer_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="merge_credentialing_addresses_into_customer_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingFinalTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="merge_credentialing_addresses_into_customer_table",
        get_logs=True,
    )

    extract_physician_race_ethnicity = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="extract_physician_race_ethnicity",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config,sftp],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPUnicodeTextFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="extract_physician_race_ethnicity",
        get_logs=True,
    )

    create_physician_race_ethnicity_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_physician_race_ethnicity_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.race_ethnicity.transform.RaceEthnicityTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_physician_race_ethnicity_table",
        get_logs=True,
    )

    create_credentialing_customer_institution_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_credentialing_customer_institution_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerInstitutionTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_credentialing_customer_institution_table",
        get_logs=True,
    )

    create_credentialing_customer_business_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_credentialing_customer_business_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerBusinessTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_credentialing_customer_business_table",
        get_logs=True,
    )

    create_residency_program_physician_table = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="create_residency_program_physician_table",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.link.transform.ResidencyProgramPhysicianTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="create_residency_program_physician_table",
        get_logs=True,
    )

    load_tables_into_database = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="load_tables_into_database",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, oneview_database],
        env_vars=dict(TASK_CLASS='datalabs.etl.orm.load.ORMLoaderTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="load_tables_into_database",
        get_logs=True,
    )

extract_ppd >> create_physician_table >> load_tables_into_database
extract_type_of_practice >> create_type_of_practice_table >> load_tables_into_database
extract_present_employment >> create_present_employment_table >> load_tables_into_database
extract_major_professional_activity >> create_major_professional_activity_table >> load_tables_into_database
extract_federal_information_processing_standard_county >> create_federal_information_processing_standard_county_table >> load_tables_into_database
extract_core_based_statistical_area >> create_core_based_statistical_area_table >> load_tables_into_database
extract_specialty >> create_specialty_table
create_physician_table >> remove_unused_specialties
create_specialty_table >> remove_unused_specialties
remove_unused_specialties >> load_tables_into_database
extract_residency >> create_residency_program_tables >> load_tables_into_database
extract_iqvia >> create_business_and_provider_tables >> load_tables_into_database
extract_credentialing_addresses >> create_credentialing_addresses_table
extract_credentialing_main >> create_credentialing_customer_product_and_order_tables
create_credentialing_addresses_table >> merge_credentialing_addresses_into_customer_table
create_credentialing_customer_product_and_order_tables >> merge_credentialing_addresses_into_customer_table
merge_credentialing_addresses_into_customer_table >> load_tables_into_database
extract_physician_race_ethnicity >> create_physician_race_ethnicity_table >> load_tables_into_database
merge_credentialing_addresses_into_customer_table >> create_credentialing_customer_institution_table
create_residency_program_tables >> create_credentialing_customer_institution_table
create_credentialing_customer_institution_table >> load_tables_into_database
merge_credentialing_addresses_into_customer_table >> create_credentialing_customer_business_table
create_business_and_provider_tables >> create_credentialing_customer_business_table
create_credentialing_customer_business_table >> load_tables_into_database
create_residency_program_tables >> create_residency_program_physician_table
create_physician_table >> create_residency_program_physician_table
create_residency_program_physician_table >> load_tables_into_database
