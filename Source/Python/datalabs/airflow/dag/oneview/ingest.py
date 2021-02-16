from airflow import DAG
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.utils.dates import days_ago
from kubernetes.client import models as k8s


etl_config = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name='oneview-type-of-practice'))
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

with DAG(
        dag_id='type_of_practice',
        default_args={'owner': 'airflow'},
        schedule_interval=None,
        start_date=days_ago(2),
        tags=['OneView'],
) as dag:

    ppd_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="ppd_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="ppd_extractor",
        get_logs=True,
    )

    ppd_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="ppd_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.oneview.ppd.transform.PPDTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="ppd_transformer",
        get_logs=True,
    )

    type_of_practice_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="type_of_practice_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="type_of_practice_extractor",
        get_logs=True,
    )

    type_of_practice_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        name="type_of_practice_transformer",
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="type_of_practice_transformer",
        get_logs=True,
    )

    present_employment_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="present_employment_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="present_employment_extractor",
        get_logs=True,
    )

    present_employment_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name = "present_employment_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="present_employment_transformer",
        get_logs=True,
    )

    major_professional_activity_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="major_professional_activity_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="major_professional_activity_extractor",
        get_logs=True,
    )

    major_professional_activity_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="major_professional_activity_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="major_professional_activity_transformer",
        get_logs=True,
    )

    federal_information_processing_standard_county_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="federal_information_processing_standard_county_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.http.extract.HTTPFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="federal_information_processing_standard_county_extractor",
        get_logs=True,
    )

    federal_information_processing_standard_county_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="federal_information_processing_standard_county_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.reference.transform.FederalInformationProcessingStandardCountyTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="federal_information_processing_standard_county_transformer",
        get_logs=True,
    )

    core_based_statistical_area_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="core_based_statistical_area_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.http.extract.HTTPUnicodeTextFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="core_based_statistical_area_extractor",
        get_logs=True,
    )

    core_based_statistical_area_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="core_based_statistical_area_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="core_based_statistical_area_transformer",
        get_logs=True,
    )

    specialty_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="specialty_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, aims],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_extractor",
        get_logs=True,
    )

    specialty_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="specialty_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_transformer",
        get_logs=True,
    )

    specialty_merge_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="specialty_merge_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.reference.transform.SpecialtyMergeTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="specialty_merge_transformer",
        get_logs=True,
    )

    residency_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="residency_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, sftp],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPUnicodeTextFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="residency_extractor",
        get_logs=True,
    )

    residency_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="residency_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.kubernetes.ETLComponentTaskWrapper'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="residency_transformer",
        get_logs=True,
    )

    iqvia_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="iqvia_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="iqvia_extractor",
        get_logs=True,
    )

    iqvia_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="iqvia_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.iqvia.transform.IQVIATransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="iqvia_transformer",
        get_logs=True,
    )

    credentialing_main_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, ods],
        env_vars=dict(TASK_CLASS='datalabs.etl.jdbc.extract.JDBCExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_extractor",
        get_logs=True,
    )

    credentialing_main_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_transformer",
        get_logs=True,
    )

    credentialing_addresses_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_addresses_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config, sftp],
        env_vars=dict(TASK_CLASS='datalabs.etl.sftp.extract.SFTPFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_addresses_extractor",
        get_logs=True,
    )

    credentialing_addresses_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_addresses_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.transform.PassThroughTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_addresses_transformer",
        get_logs=True,
    )

    credentialing_merge_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_merge_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.credentialing.transform.CredentialingFinalTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_merge_transformer",
        get_logs=True,
    )

    physician_race_ethnicity_extractor = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="physician_race_ethnicity_extractor",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=[etl_config,sftp],
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.sftp.extract.SFTPUnicodeTextFileExtractorTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="physician_race_ethnicity_extractor",
        get_logs=True,
    )

    physician_race_ethnicity_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="physician_race_ethnicity_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.race_ethnicity.transform.RaceEthnicityTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="physician_race_ethnicity_transformer",
        get_logs=True,
    )

    credentialing_customer_institution_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_customer_institution_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerInstitutionTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_customer_institution_transformer",
        get_logs=True,
    )

    credentialing_customer_business_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="credentialing_customer_business_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.link.transform.CredentialingCustomerBusinessTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="credentialing_customer_business_transformer",
        get_logs=True,
    )

    residency_program_physician_transformer = KubernetesPodOperator(
        namespace='hsg-data-labs-dev',
        image='docker-registry.default.svc:5000/hsg-data-labs-dev/datalabs-master:1.0.0',
        name="residency_program_physician_transformer",
        cmds=['python', 'task.py', '{{ task_instance_key_str }}'],
        env_from=etl_config,
        env_vars=dict(TASK_WRAPPER_CLASS='datalabs.etl.oneview.link.transform.ResidencyProgramPhysicianTransformerTask'),
        do_xcom_push=True,
        is_delete_operator_pod=True,
        in_cluster=True,
        task_id="residency_program_physician_transformer",
        get_logs=True,
    )

ppd_extractor >> ppd_transformer
present_employment_extractor >> present_employment_transformer
major_professional_activity_extractor >> major_professional_activity_transformer
federal_information_processing_standard_county_extractor >> federal_information_processing_standard_county_transformer
core_based_statistical_area_extractor >> core_based_statistical_area_transformer
specialty_extractor >> specialty_transformer
ppd_transformer >> specialty_merge_transformer
specialty_transformer >> specialty_merge_transformer
residency_extractor >> residency_transformer
iqvia_extractor >> iqvia_transformer
credentialing_addresses_extractor >> credentialing_addresses_transformer
credentialing_main_extractor >> credentialing_main_transformer
credentialing_addresses_transformer >> credentialing_merge_transformer
credentialing_main_transformer >> credentialing_merge_transformer
physician_race_ethnicity_extractor >> physician_race_ethnicity_transformer
credentialing_merge_transformer >> credentialing_customer_institution_transformer
residency_transformer >> credentialing_customer_institution_transformer
credentialing_merge_transformer >> iqvia_transformer
residency_transformer >> residency_program_physician_transformer
ppd_transformer >> residency_program_physician_transformer
