import os
from glob import glob
from datalabs.analysis.humach.survey.archive import HumachResultsArchive
import logging
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class HumachResultsIngester:
    def __init__(self, archive: HumachResultsArchive):
        self.archive = archive
        self.file_input_directory_standard = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/standard'
        self.file_input_directory_standard_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/standard/archive'

        self.file_input_directory_validation = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/validation'
        self.file_input_directory_validation_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/validation/archive'

        self.file_input_directory_samples = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/samples'
        self.file_input_directory_samples_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/samples/archive'

    def get_standard_result_files(self):
        files = glob(self.file_input_directory_standard + '/*.xls')
        files = [f.replace('\\', '/') for f in files]
        return files

    def get_validation_result_files(self):
        files = glob(self.file_input_directory_validation + '/*.xlsx')
        files = [f.replace('\\', '/') for f in files]
        return files

    def get_sample_files(self):
        files = glob(self.file_input_directory_samples + '/*.xlsx')
        files = [f.replace('\\', '/') for f in files]
        return files

    # ingest_standard and ingest_validation are different because standard and validation result files have
    # different file types (xls vs xlsx)
    def ingest_standard(self):
        files = self.get_standard_result_files()
        already_processed = [os.path.split(p)[-1] for p in os.listdir(self.file_input_directory_standard_archive)]
        print(already_processed)
        for file in files:
            print(file)
            filename = os.path.split(file)[-1]
            print(filename)
            if filename in already_processed:
                LOGGER.info(f'{file} ALREADY PROCESSED PREVIOUSLY. SKIPPING.')
            else:
                LOGGER.info(f'PROCESSING FILE: {file}')
                #self.archive.ingest_result_file(table='humach_result', file_path=file)
                LOGGER.info('SUCCESS.')

    def ingest_validation(self):
        files = self.get_validation_result_files()
        for file in files:
            print(file)
            LOGGER.info(f'PROCESSING FILE: {file}')
            self.archive.ingest_result_file(table='validation_result', file_path=file)
            LOGGER.info('SUCCESS.')

    def ingest_samples(self):
        files = self.get_sample_files()
        print(files)
        for file in files:
            try:
                LOGGER.info(f'PROCESSING FILE: {file}')
                self.archive.ingest_sample_file(file_path=file)
                LOGGER.info('SUCCESS.')
            except Exception as e:
                LOGGER.info('FAILED:', e)


archive = HumachResultsArchive()
archive._load_environment_variables()
os.environ['ARCHIVE_DB_PATH'] = 'C://Users/glappe/PycharmProjects/hsg-data-labs/Sandbox/HumachSurveys/HumachSurveys.db'
ingester = HumachResultsIngester(archive=archive)
ingester.ingest_standard()
# ingester.ingest_validation()

