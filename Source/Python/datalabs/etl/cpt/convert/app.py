import enum
import logging

import datalabs.curate.cpt as cpt
import datalabs.etl.etl as etl
from   datalabs.etl.extract import Extractor
from   datalabs.etl.load import Loader

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class Configuration:
    extractor: Extractor
    loader: Loader


class ETL(etl.ETL):
    def __init__(self, configuration):
        self._configuration = configuration

    def run(self):
        texts = self._extract_texts()

        for text_type
        csv_dataset = self._transform_text_to_csv_dataset(texts)

        self._load_csv_data(csv_dataset)

    def _extract_text_data(self):
        pass

    @classmethod
    def _transform_text_to_csv_data(cls, texts):
        pass

    def _load_csv_data(csv_dataset):
        pass


def main(file_type):
    files, descriptors = get_s3_files(file_type)
    df = parse_s3_txt(files, descriptors, file_type)
    csv_file, output_file = df_to_csv(df, file_type, descriptors)
    push_csv(csv_file, output_file)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "done",
        }),
    }


def get_s3_files(file_type):
    s3 = boto3.client('s3')
    if file_type == FileType.CPT:
        file_list, file_descriptions = get_cpt_files()
        return file_list, file_descriptions

    elif file_type == FileType.ClinicalDescriptor:
        cliniciandescriptor_obj = s3.get_object(Bucket=os.environ['ingestion_bucket'], Key=os.environ['c_path'])
        file_list = cliniciandescriptor_obj
        return file_list, ['clinicaldescriptors']

    elif file_type == FileType.Modifier:
        temp = tempfile.NamedTemporaryFile()
        s3.download_file(os.environ['ingestion_bucket'], os.environ['s3_path'] + 'MODUL.txt', temp.name)
        return temp.name, ['modifier']


def parse_s3_txt(file_list, file_descriptor, file_type):
    if file_type == FileType.ClinicalDescriptor:
        cd_df = cpt.clinical_descriptor.parse_descriptors(file_list)
        return cd_df

    elif file_type == FileType.Modifier:
        file_object = cpt.modifier.ModifierFileParser()
        mod_df = file_object.parse(file_list)
        return mod_df

    elif file_type == FileType.CPT:
        cpt_df = cpt.description.parse_cpt_file(file_list, file_descriptor)
        return cpt_df


def df_to_csv(df, file_type, file_descriptor):
    csv_name = []
    if file_type == FileType.ClinicalDescriptor:
        output_file = ['ClinicianDescriptor.csv']
        with tempfile.NamedTemporaryFile() as temp:
            df.to_csv(temp.name + '.csv', sep='\t')
        csv_name.append(temp.name)
        return csv_name, output_file

    elif file_type == FileType.Modifier:
        output_file = ['modifier.csv']
        with tempfile.NamedTemporaryFile() as temp:
            df.to_csv(temp.name + '.csv', sep='\t')
        csv_name.append(temp.name)
        return csv_name, output_file

    elif file_type == FileType.CPT:
        csv_files, output_file = cpt.cpt_to_csv(df, file_descriptor)
        return csv_files, output_file


def push_csv(csv_files, output_file):
    s3 = boto3.client('s3')
    for csv in csv_files:
        s3.upload_file(csv + '.csv', os.environ['processed_bucket'], output_file[csv_files.index(csv)])

    LOGGER.info('Upload Successful')


def get_cpt_files():
    s3 = boto3.client('s3')
    imported_file = []
    file_list = ['MEDU.txt', 'SHORTU.txt', 'LONGUF.txt', 'LONGULF.txt', 'LONGUT.txt', 'LONGULT.txt']
    file_descriptors = [FileDescriptor('medium_description', False), FileDescriptor('short_description', False),
                        FileDescriptor('longuf_description', False), FileDescriptor('longulf_description', False),
                        FileDescriptor('longut_description', True), FileDescriptor('longult_description', True)]
    for file in file_list:
        with tempfile.NamedTemporaryFile(mode='r+') as temp:
            s3.download_file(os.environ['ingestion_bucket'], os.environ['s3_path'] + file, temp.name)
        imported_file.append(temp.name)

    return imported_file, file_descriptors


