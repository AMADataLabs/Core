import boto3
import os
import logging
import tempfile
import clinical_descriptors
import cpt
import modifier

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
LOGGER.info('Upload Successful')


def main(File_type):
    files, descriptors = get_s3_files(File_type)
    df = parse_s3_txt(files, descriptors, File_type)
    csv_file, output_file = df_to_csv(df, File_type, descriptors)
    push_csv(csv_file, output_file)


def parse_s3_txt(file_list, file_descriptor, FileType):
    if FileType == 'clinicalDescriptors':
        cd_df = clinical_descriptors.parse_descriptors(file_list)
        return cd_df

    elif FileType == 'modifiers':
        file_object = modifier.ModifierFileParser()
        mod_df = file_object.parse(file_list)
        return mod_df

    elif FileType == 'cpt':
        cpt_df = cpt.parse_cpt_file(file_list, file_descriptor)
        return cpt_df


def df_to_csv(df, FileType, file_descriptor):
    csv_name = []
    if FileType == 'clinicalDescriptors':
        output_file = ['ClinicianDescriptor.csv']
        with tempfile.NamedTemporaryFile() as temp:
            df.to_csv(temp.name + '.csv', sep='\t')
        csv_name.append(temp.name)
        return csv_name, output_file

    elif FileType == 'modifiers':
        output_file = ['modifier.csv']
        with tempfile.NamedTemporaryFile() as temp:
            df.to_csv(temp.name + '.csv', sep='\t')
        csv_name.append(temp.name)
        return csv_name, output_file

    elif FileType == 'cpt':
        csv_files, output_file = cpt.cpt_to_csv(df, file_descriptor)
        return csv_files, output_file


def push_csv(csv_files, output_file):
    s3 = boto3.client('s3')
    for csv in csv_files:
        s3.upload_file(csv + '.csv', os.environ['processed_bucket'], output_file[csv_files.index(csv)])

    LOGGER.info('Upload Successful')


def get_s3_files(filetype):
    s3 = boto3.client('s3')
    if filetype == 'cpt':
        file_list, file_descriptions = cpt.get_cpt_files()
        return file_list, file_descriptions

    elif filetype == 'clinicalDescriptors':
        clinicianDescriptor_obj = s3.get_object(Bucket=os.environ['ingestion_bucket'], Key=os.environ['c_path'])
        file_list = clinicianDescriptor_obj
        return file_list, ['clinicalDescriptors']

    elif filetype == 'modifiers':
        temp = tempfile.NamedTemporaryFile()
        s3.download_file(os.environ['ingestion_bucket'], os.environ['s3_path'] + 'MODUL.txt', temp.name)

        return temp.name, ['modifier']

    else:
        LOGGER.info('File type does not exist')


main('cpt')
