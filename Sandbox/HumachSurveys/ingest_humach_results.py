from glob import glob
from HumachSurveys.HumachResultsArchive import HumachResultsArchive
import logging
logging.basicConfig(level=logging.DEBUG)
import settings


class HumachStandardResultsIngester:
    def __init__(self, archive: HumachResultsArchive):
        self.archive = archive
        self.file_input_directory_standard = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/standard'
        self.file_input_directory_standard_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/standard/archive'

        self.file_input_directory_validation = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/validation'
        self.file_input_directory_validation_archive = 'U:/Source Files/Data Analytics/Data-Science/Data/HumachSurveys/validation/archive'

        self.logger = logging.getLogger('info')

    def get_standard_result_files(self):
        files = glob(self.file_input_directory_standard + '/*.xls')
        files = [f.replace('\\', '/') for f in files]
        return files

    def get_valdiation_result_files(self):
        files = glob(self.file_input_directory_validation + '/*.xls')
        files = [f.replace('\\', '/') for f in files]
        return files

    def ingest_standard(self):

        files = self.get_standard_result_files()

        for file in files:
            #try:
            self.logger.info(f'PROCESSING FILE: {file}')
            self.archive.ingest_result_file(table='results_standard', file_path=file)
            self.logger.info('SUCCESS.')
            #except Exception:
            #    self.logger.info('FAILED.')

    def ingest_validation(self):
        pass


archive = HumachResultsArchive(database='HumachSurveys.db')
ingester = HumachStandardResultsIngester(archive=archive)

ingester.ingest_standard()



