""" Check the quality of disciplinary action data. """
from   abc import ABC, abstractmethod
from   collections import Counter
import csv
from   dataclasses import dataclass
from   datetime import datetime
import functools
import glob
import itertools
import json
import logging
import os
import pandas
import re
import time

from PyPDF2 import PdfFileReader

import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class Loggers:
    file_error: logging.Logger
    failure_count: logging.Logger


@dataclass
class LogPaths:
    failure_count: str
    file_error: str


@dataclass
class FailureCounts:
    total: int = 0
    name_format: int = 0
    completeness: int = 0
    file_exists: int = 0
    file_quality: int = 0
    no_data_pdf: int = 0
    no_data_duplicate: int = 0

    def __add__(self, other):
        count_map = {key:getattr(self, key) + getattr(other, key) for key in self.__dataclass_fields__.keys()}

        return FailureCounts(**count_map)

    def __iadd__(self, other):
        for field in self.__dataclass_fields__.keys():
            setattr(self, field, getattr(self, field) + getattr(other, field))


class FileValidator(ABC):
    @abstractmethod
    def _file_name_is_valid(self, file_name):
        pass

    @abstractmethod
    def _file_contents_is_valid(self, file_name):
        pass


class IgnoreNameFileValidatorMixin:
    def _file_name_is_valid(self, file_name):
        return True


class IgnoreContentsFileValidatorMixin:
    def _file_contents_is_valid(self, file_name):
        return True


class PDFFileContentsValidatorMixin:
    def _file_contents_is_valid(self, file_name):
        # TODO: Page is distorted or not
        is_valid = True

        with file in open(file_name, 'rb'):
            pdf = PdfFileReader(open(file_name, 'rb'))

        for page_number, page in enumerate(pdf.pages):
            if _page_is_blank(page):
                LOGGER.info('Page %d of %s is blank.', page_number, file_name)
                is_valid = False

        return is_valid


class SLFileValidator(PDFFileContentsValidatorMixin, FileValidator):
    def _file_name_is_valid(self, file_name):
        is_valid = False
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_SL.pdf'

        if re.match(pattern, file_name) is not None:
            is_valid = True
        else:
            if file_name.split('-')[0] == 'DHHS':
                pattern = r'DHHS-\S*_SL.pdf'
                if re.match(pattern, file_name) is not None:
                    is_valid = True


class NLFileValidator(PDFFileContentsValidatorMixin, FileValidator):
    def _file_name_is_valid(self, file_name):
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_NL.pdf'

        if re.match(pattern, file_name) is not None:
            return True


class BOFileValidator(PDFFileContentsValidatorMixin, FileValidator):
    def _file_name_is_valid(self, file_name):
        is_valid = False

        if file_name.split('-')[0] == 'DHHS':
            pattern = r'DHHS-\S*_BO.pdf'
            if re.match(pattern, file_name) is not None:
                is_valid = True

        pattern = r'\S*-[0-9]*_[0-9]*_[0-9]*_BO.pdf'
        if re.match(pattern, file_name) is not None:
            is_valid = True
        else:
            pattern = r'\S*-[0-9]*_[0-9]*_[0-9]*_BO_#[0-9].pdf'
            if re.match(pattern, file_name) is not None:
                is_valid = True

    @classmethod
    def _page_is_blank(cls, page):
        return page.getContents() is None


class QAFileValidator(IgnoreNameFileValidatorMixin, PDFFileContentsValidatorMixin, FileValidator):
    def _file_contents_is_valid(self, file_name):
        data = pandas.read_csv(file_name)

        return np.all(pandas.isnull(data))


class MFileValidator(IgnoreNameFileValidatorMixin, IgnoreContentsFileValidatorMixin, FileValidator):
    pass


class FileValidatorFactory():
    VALIDATORS = dict(
        SL=SLFileValidator,
        NL=FileValidator,
        BO=BOFileValidator,
        QA=QAFileValidator,
        M=MFileValidator,
    )

    @classmethod
    def create_validator(cls, file_type):
        if file_type not in VALIDATOR_TABLE:
            raise ValueError(f"File type '{file_type}' is not supported.")

        return VALIDATORS[file_type]()


class DataValidator:
    def __init__(self, latest_actions_path):
        self._latest_actions_path = latest_actions_path
        self._action_source_folders = action_source_folders
        self._no_data_folders = no_data_folders

    def validate(self):
        failure_counts = []
        valid_update_folders = self._get_valid_update_folders()

        if self._data_file_composition_is_correct(valid_update_folders):
            LOGGER.info('Disciplinary action folders are correct')
            LOGGER.debug('next step: check mandatory files contents in the folder')

            failure_counts = self._validate_data_files(valid_update_folders)
        else:
            failure_counts.append(FailureCounts(file_exists=1))

    def _get_valid_update_folders(self):
        return [f for f in self._action_source_folders if f != 'no_data']

    def _data_file_composition_is_correct(self.valid_update_folders) -> bool:
        is_correct = True

        while is_correct:
            is_correct = self._partial__data_file_composition_is_correct(valid_update_folders.pop(0))

        return is_correct

    def _validate_data_files(self, valid_update_folders):
        for folder in valid_update_folders:
            failure_counts = self._validate_folder_data(os.path.join(self._latest_actions_path, folder))

        return functools.reduce(lambda a, b: a + b, failure_counts)

    def _partial__data_file_composition_is_correct(self, folder):
        folder_path = os.path.join(self._latest_actions_path,  folder)
        all_files = os.listdir(folder_path)
        pdf_files = [file for file in os.listdir(folder_path) if not self._file_is_a_word_document(file)]
        composition_is_correct = False

        if len(pdf_files) == len(all_files):
            composition_is_correct = self._required_data_file_types_are_present(folder)

        return composition_is_correct

    @classmethod
    def _validate_folder_data(cls, folder):
        failure_counts = []

        for file in [f for f in os.listdir(folder) if not f.startswith('.')]:
            file_path = os.path.join(folder, file)

            failure_count.append(cls._validate_data_file(file_path))

        return functools.reduce(lambda a, b: a + b, failure_counts)

    @classmethod
    def _file_is_a_word_document(cls, file):
        is_word_doc = False

        if file.split('.')[-1] in ['docx', 'doc']:
            LOGGER.info('There is a non-pdf file: %s', file)
            is_word_doc = True

        return is_word_doc

    @classmethod
    def _required_data_file_types_are_present(cls, folder):
            folder_prefix = folder.rsplit('_', 5)[0]  # Example: NV_MD_SummaryList
            expected_file_types = self._required_file_types[folder_prefix]
            file_types = set([cls._get_doc_type(file) for file in pdf_files])
            file_types_are_present = False

            if file_types == expected_file_types:
                file_types_are_present = True
            else:
                LOGGER.info('Expected file types %s for folder %s, but found only %s', expected_file_types, folder, file_types)

            return file_types_are_present

    @classmethod
    def _validate_data_file(cls, file_path, logger):
        failure_counts = FailureCounts()
        file_name = os.path.basename(file)
        file_type = cls._get_doc_type(file_name)
        failure_counts = []

        failure_counts.append(_validate_file_name(file_name, file_type, logger))

        failure_counts.append(_validate_file_contents(file_path, file_type, logger))

        return functools.reduce(lambda a, b: a + b, failure_counts)

    @classmethod
    def _get_doc_type(cls, file_name) -> str:
        file_type = file_name.rsplit('.', 1)[0].rsplit('_', 1)[-1]

        # if there are multiple BO for same physician, need adjust to get 'BO'
        # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
        if re.match(r'#[0-9]', file_type) is not None:
            file_type = file_name.split('.')[0].rsplit('_', 2)[-2]

        return file_type

    @classmethod
    def _validate_file_name(cls, file_name, file_type, logger) -> FailureCounts:
        failure_counts = FailureCounts()

        if not cls._file_name_is_valid(file_name, file_type):
            LOGGER.info('File name format is not right: %s', file_name)
            failure_counts.name_format = 1

            logger.info('%s, name_format', file_name)

        return failure_counts

    @classmethod
    def _validate_file_contents(cls, file_path, file_type, logger) -> FailureCounts:
        failure_counts = FailureCounts()

        if not cls._file_contents_is_valid(file_path, file_type):
            LOGGER.info('%s file %s is not right', file_type, file_name)
            failure_counts.file_quality = 1

            logger.info('%s, file_quality - %s', file_name, "QA" if file_type == "QA" else "blank page")

        return failure_counts

    @classmethod
    def _file_name_is_valid(cls, file_name, file_type) -> bool:
        validator = FileValidatorFactory.create_validator(file_type)

        return validator._file_name_is_valid(file_name)

    @classmethod
    def _file_contents_is_valid(cls, file_name, file_type) -> bool:
        validator = FileValidatorFactory.create_validator(file_type)

        return validator._file_contents_is_valid(file_name)


class NewlyProcuredDataValidator(DataValidator):
    def validate(self) -> FailureCounts:
        failure_counts = None

        LOGGER.debug('This folder is a new procurement')

        if self._data_is_complete():
            failure_counts = super().validate()
        else:
            failure_counts = FailureCounts(completeness=1)

        return failure_counts

    def _data_is_complete(self) -> bool:
        is_complete = False

        if not self._pdfs_are_present() and self._folder_count_is_correct() and self._all_folders_are_unique():
            is_complete = True

        return is_complete

    def _pdfs_are_present(self):
        pdf_count = self._count_pdfs(self._no_data_folders)
        _pdfs_are_present = False

        if count > 0:
            _pdfs_are_present = True

        return _pdfs_are_present

    def _folder_count_is_correct(self):
        total_folder_count = len(self._action_source_folders) + len(self._no_data_folders)
        count_is_correct = False

        if total_folder_count == 69:
            count_is_correct = True
        else:
            LOGGER.info('Total folder count is not right: %d', total_folder_count)

        return count_is_correct

    def _all_folders_are_unique(self):
        all_folders = os.path.join(self._action_source_folders, self._no_data_folders)
        unique_folders = set(all_folders)
        are_unique = False

        if len(all_folders) == len(unique_folders):
            are_unique = True
        else:
            LOGGER.info('Duplicate folder found in no_data folder.')

        return are_unique

    # CLEAN CODE NOTE: Consider using class methods for generic functions. This eliminates the possibility
    # of side effects due to shared class instance data. Pylint will point obvious candidates out
    # due to now "self" use, but a simple function with one parameter can also be a candidate even
    # if that single parameter is an instance variable.
    @classmethod
    def _count_pdfs(cls, folders):
        count = 0

        for folder in folders:
            files = os.listdir(folder)

            if file[-4:] == '.pdf':
                count += 1

        return count


class RebaselinedDataValidator(DataValidator):
    pass


class DisciplinaryDataQualityChecker:
    def __init__(self):
        self._data_base_path = None
        self._required_file_types = None
        self._loggers = None

    def run(self):
        self._data_base_path = os.environ.get('DATA_BASE_PATH')
        self._required_file_types = {
            prefix: set(group['types'])
            for group in json.load(os.environ.get('REQUIRED_FILE_TYPES')
            for prefix in group
        }

        log_paths = LogPaths(
            failure_count=os.environ.get('COUNT_LOG'),
            file_error=os.environ.get('FILE_LOG')
        )
        self._setup_loggers(log_paths)

        if self._new_data_available():
            self._check_disciplinary_action_data_quality()
        else:
            LOGGER.info('No new data to check.')

    def _setup_loggers(self, log_paths) -> Loggers:
        loggers = Loggers(
            failure_count=logging.getLogger('Failure Counts'),
            file_error=logging.getLogger('File Errors')
        )
        LOGGER.debug('Loggers: %s', loggers)

        for field in log_paths.__dataclass_fields__:
            self._setup_logger(getattr(loggers, field), getattr(log_paths, field))

        retrn loggers

    def _new_data_available(self) -> bool:
        """ check if new data was uploaded to the folder of weekly results """
        date_last_updated = _get_date_last_updated()
        LOGGER.info('Last folder uploaded on %s.', date_last_updated)
        today = datetime.utcnow().date()

        return date_last_updated == today

    def _check_disciplinary_action_data_quality(self):
        failure_counts = None
        latest_actions_path = self._get_latest_actions_path()
        action_source_folders = self._get_folder_contents(self._latest_actions_path)
        no_data_path = os.path.join(self._latest_actions_path, 'no_data')
        no_data_folders = [os.path.join(no_data_path, path) for path in self._get_folder_contents(no_data_path)]
        validator = None

        LOGGER.info('New disciplinary action folders uploaded: %s', self._latest_actions_path)

        if self._is_newly_procured_data():
            LOGGER.debug('This folder is a newly-procured data folder')
            validator = NewlyProcuredDataValidator(latest_actions_path, action_source_folders, no_data_folders)
        else:
            LOGGER.debug('This folder is a re-baselined data folder')
            validator = RebaselinedDataValidator(latest_actions_path, action_source_folders, no_data_folders)

        failure_counts = validator.validate()

        _log_failure_counts(self._loggers.failure_count, failure_counts)

    @classmethod
    def _setup_logger(cls, logger, log_path):
        file_handler = logging.FileHandler(log_path)

        stream_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s,%(message)s', "%Y-%m-%d")
        formatter.converter = time.gmtime

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        logger.setLevel(logging.INFO)

    def _get_date_last_updated(self):
        mod_time_in_seconds = os.path.getmtime(self._data_base_path)

        mod_datetime = datetime.utcfromtimestamp(mod_time_in_seconds)

        return mod_datetime.date()

    def _get_latest_actions_path(self) -> list:
        files = glob.glob(os.path.join(self._data_base_path, '/*'))

        return max(files, key=os.path.getctime)

    def _get_folder_contents(self, path) -> list:
        return [d for d in os.listdir(path) if not d.startswith('.')]

    @classmethod
    def _is_newly_procured_data(cls) -> bool:
        if len(self._action_source_folders) + len(self._no_data_folders) == 69:
            return True
        return False


if __name__ == '__main__':
    DisciplinaryDataQualityChecker().run()
