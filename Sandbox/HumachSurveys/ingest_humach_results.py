from glob import glob
from HumachSurveys.HumachResultsArchive import HumachResultsArchive
import logging
logging.basicConfig(level=logging.INFO)
import settings


class HumachResultsIngester:
    def __init__(self, archive: HumachResultsArchive):
        self.archive = archive
        self.file_input_directory_standard = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/standard'
        self.file_input_directory_standard_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/standard/archive'

        self.file_input_directory_validation = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/validation'
        self.file_input_directory_validation_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/validation/archive'

        self.file_input_directory_samples = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/samples'
        self.file_input_directory_samples_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/samples/archive'

        self.logger = logging.getLogger('info')

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

        for file in files:
            try:
                self.logger.info(f'PROCESSING FILE: {file}')
                self.archive.ingest_result_file(table='results_standard', file_path=file)
                self.logger.info('SUCCESS.')
            except Exception as e:
                self.logger.info('FAILED:', e)

    def ingest_validation(self):

        files = self.get_validation_result_files()
        for file in files:
            try:
                self.logger.info(f'PROCESSING FILE: {file}')
                self.archive.ingest_result_file(table='results_validation', file_path=file)
                self.logger.info('SUCCESS.')
            except Exception as e:
                self.logger.info('FAILED:', e)

    def ingest_samples(self):

        files = self.get_sample_files()
        for file in files:
            try:
                self.logger.info(f'PROCESSING FILE: {file}')
                self.archive.ingest_sample_file(file_path=file)
                self.logger.info('SUCCESS.')
            except Exception as e:
                self.logger.info('FAILED:', e)



archive = HumachResultsArchive(database='HumachSurveys.db')

ingester = HumachResultsIngester(archive=archive)
ingester.ingest_samples()


