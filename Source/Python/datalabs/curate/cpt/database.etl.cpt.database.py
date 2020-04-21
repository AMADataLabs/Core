import boto3
import logging
import os
import tempfile
from rds_tables import CreateRDS

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.info('Upload Successful')


def main(table_type):
    file = get_s3_files(table_type)
    create_table(table_type)
    push_table(table_type, file)


def get_s3_files(table_type):
    s3 = boto3.client('s3')
    if table_type == 'modifiers':
        temp = tempfile.NamedTemporaryFile(suffix='.csv')
        s3.download_file(os.environ['processed_bucket'], os.environ['mod_key'], temp.name)

    elif table_type == 'cpt':
        temp = tempfile.NamedTemporaryFile(suffix='.csv')
        s3.download_file(os.environ['processed_bucket'], os.environ['cpt_key'], temp.name)

    elif table_type == 'clinicaldescriptors':
        temp = tempfile.NamedTemporaryFile(suffix='.csv')
        s3.download_file(os.environ['processed_bucket'], os.environ['descriptors_key'], temp.name)

    else:
        LOGGER.info('File Does Not exist')

    return temp.name


def create_table(table_type):
    rds_object = CreateRDS()
    if table_type == 'modifiers':
        rds_object.create_schema()
        rds_object.create_modifier_type_table()
        rds_object.create_modifier_table()

    elif table_type == 'cpt':
        rds_object.create_schema()
        rds_object.create_cpt_table()

    elif table_type == 'clinicaldescriptors':
        rds_object.create_schema()
        rds_object.create_descriptor_table()


def push_table(table_type, file):
    rds_object = CreateRDS()
    if table_type == 'modifiers':
        rds_object.push_modifier_type_table()
        rds_object.push_modifiers_table(file)

    elif table_type == 'cpt':
        rds_object.push_cpt_table(file)

    elif table_type == 'clinicaldescriptors':
        rds_object.push_descriptor_table(file)
