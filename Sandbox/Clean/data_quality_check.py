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

# logging.basicConfig()
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
    def file_name_is_valid(self, file_name):
        pass

    @abstractmethod
    def file_contents_is_valid(self, file_name):
        pass


class IgnoreNameFileValidatorMixin:
    def file_name_is_valid(self, file_name):
        return True


class IgnoreContentsFileValidatorMixin:
    def file_contents_is_valid(self, file_name):
        return True


class PDFFileContentsValidatorMixin:
    def file_contents_is_valid(self, file_name):
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
    def file_name_is_valid(self, file_name):
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
    def file_name_is_valid(self, file_name):
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_NL.pdf'

        if re.match(pattern, file_name) is not None:
            return True


class BOFileValidator(PDFFileContentsValidatorMixin, FileValidator):
    def file_name_is_valid(self, file_name):
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
    def file_contents_is_valid(self, file_name):
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


def main():
    data_base_path = os.environ.get('DATA_BASE_PATH')
    required_file_types = {prefix: set(group['types']) for group in json.load(os.environ.get('REQUIRED_FILE_TYPES') for prefix in group)}
    log_paths = LogPaths(
        failure_count=os.environ.get('COUNT_LOG'),
        file_error=os.environ.get('FILE_LOG')
    )

    loggers = setup_loggers(log_paths)

    date_last_updated = modification_date(data_base_path)


    if new_data_available(date_last_updated):
        check_disciplinary_action_data_quality(data_base_path, required_file_types, loggers)
    else:
        LOGGER.info('No new folders uploaded. Last folder uploaded on %s.', date_last_updated)


def setup_loggers(log_paths) -> Loggers:
    loggers = Loggers(
        failure_count=logging.getLogger('Failure Counts'),
        file_error=logging.getLogger('File Errors')
    )
    LOGGER.debug('Loggers: %s', loggers)

    for field in log_paths.__dataclass_fields__:
        LOGGER.debug('Field: %s', field)
        logger = getattr(loggers, field)
        LOGGER.debug('Logger: %s', logger)

        file_handler = logging.FileHandler(getattr(log_paths, field))

        stream_handler = logging.StreamHandler(getattr(log_paths, field))

        formatter = logging.Formatter('%(asctime)s,%(message)s', "%Y-%m-%d")
        formatter.converter = time.gmtime

        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        logger.setLevel(logging.INFO)

    return loggers


def modification_date(path):
    mod_time_in_seconds = os.path.getmtime(path)

    mod_datetime = datetime.utcfromtimestamp(mod_time_in_seconds)

    return mod_datetime.date()


def new_data_available(date_last_updated) -> bool:
    """ check if new data was uploaded to the folder of weekly results """
    today = datetime.datetime.utcnow()

    return date_last_updated == today


def check_disciplinary_action_data_quality(data_base_path, required_file_types, loggers):
    failure_counts = None
    latest_actions_path = get_latest_actions_path(data_base_path)
    action_source_folders = get_folder_contents(latest_actions_path)
    no_data_folders = get_folder_contents(no_data_path)

    LOGGER.info('New disciplinary action folders uploaded: %s', latest_actions_path)

    if is_newly_procured_data(no_data_folders, action_source_folders):
        LOGGER.debug('This folder is a newly-procured data folder')
        failure_counts = validate_newly_procured_data(latest_actions_path, action_source_folders, no_data_folders)
    else:
        LOGGER.debug('This folder is a re-baselined data folder')
        failure_counts = validate_rebaselined_data(latest_actions_path, action_source_folders, required_file_types)

    log_failure_counts(loggers.failure_count, failure_counts)


def get_latest_actions_path(data_base_path) -> list:
    files = glob.glob(os.path.join(data_base_path, '/*'))

    return max(files, key=os.path.getctime)


def get_folder_contents(path) -> list:
    return [d for d in os.listdir(path) if not d.startswith('.')]


def is_newly_procured_data(no_data_folders, action_source_folders) -> bool:
    if len(action_source_folders) + len(no_data_folders) == 69:
        return True
    return False


def validate_newly_procured_data(latest_actions_path, action_source_folders, no_data_folders) -> FailureCounts:
    failure_counts = None
    no_data_path = latest_actions_path + '/no_data'

    LOGGER.debug('This folder is a new procurement')

    if data_is_complete(action_source_folders, no_data_folders):
        failure_counts = validate_data(latest_actions_path, action_source_folders)
    else:
        failure_counts = FailureCounts(completeness=1)

    return failure_counts


def validate_rebaselined_data(latest_actions_path, action_source_folders, required_file_types) -> FailureCounts:
    return validate_data(latest_actions_path, action_source_folders)


def log_failure_counts(logger, failure_counts):
    logger.info(
        '\n{},{},{},{},{},{}, {}'.format(
            failcount, failure_counts.name_format, failure_counts.completeness,
            failure_counts.file_exists, failure_counts.file_quality, failure_counts.no_data_pdf,
            failure_counts.no_data_duplicate
        )
    )


def data_is_complete(action_source_folders, no_data_folders) -> bool:
    is_complete = False

    if not pdfs_are_present(no_data_folders) \
       and folder_count_is_correct(action_source_folders, no_data_folders) \
       and all_folders_are_unique(action_source_folders + no_data_folders):
        is_complete = True

    return is_complete


def validate_data(latest_actions_path, action_source_folders, required_file_types):
    failure_counts = []
    valid_update_folders = get_valid_update_folders(action_source_folders)

    # CLEAN CODE COMMENT: Example of why comments are risky:
    #   1) If you have to explain what a function does, either the name isn't sufficient or its burying functionality
    #      that should be at the same abstraction level as the function. Split it up.
    #   2) Comments often fall out of sync with the code they are annotating. Case in point,
    #      data_file_composition_is_correct() is not deleting anything.
    if data_file_composition_is_correct(latest_actions_path, valid_update_folders, required_file_types):
        LOGGER.info('Disciplinary action folders are correct')
        LOGGER.debug('next step: check mandatory files contents in the folder')

        failure_counts = validate_data_files(latest_actions_path, action_source_folders, valid_update_folders)
    else:
        failure_counts.append(FailureCounts(file_exists=1))


def pdfs_are_present(no_data_folders):
    pdf_count = count_pdfs(no_data_folders)
    pdfs_are_present = False

    if count > 0:
        pdfs_are_present = True

    return pdfs_are_present


def folder_count_is_correct(action_source_folders, no_data_folders):
    total_folder_count = len(action_source_folders) + len(no_data_folders)
    count_is_correct = False

    if total_folder_count == 69:
        count_is_correct = True
    else:
        LOGGER.info('Total folder count is not right: %d', total_folder_count)

    return count_is_correct


def all_folders_are_unique(all_folders):
    unique_folders = set(all_folders)
    are_unique = False

    if len(all_folders) == len(unique_folders):
        are_unique = True
    else:
        LOGGER.info('Duplicate folder found in no_data folder.')

    return are_unique


def get_valid_update_folders(action_source_folders):
    return [f for f in action_source_folders if f != 'no_data']


# CLEAN CODE COMMENT: Summary of changes:
#   1) Eliminated duplicated code
#       - get_doc_type()
#   2) Put lower-abstraction code in functions
#       - function was doing multiple things with nested structures
#   3) Used a while loop + list.pop(0) to avoid nested "if" in for loop
#       - for loops don't have a conditional clause and while loops are not great for iteration, so get creative
#   4) Used list comprehensions to eliminate an ugly for loop with a break
#       - Nested for loop was doing two different things and returning if one of those things failed
#   5) Modified JSON data and reindexed it to allow for lookups instead of an if-elif block
#       - see required_file_types.json and dict comprehension in main()
def data_file_composition_is_correct(latest_actions_path, valid_update_folders, required_file_types) -> bool:
    composition_is_correct = True

    while composition_is_correct:
        composition_is_correct = partial_data_file_composition_is_correct(latest_actions_path, valid_update_folders.pop(0), required_file_types)

    return composition_is_correct


def validate_data_files(latest_actions_path, valid_update_folders):
    for folder in valid_update_folders:
        failure_counts = validate_folder_data(latest_actions_path, folder)

    return functools.reduce(lambda a, b: a + b, failure_counts)


def count_pdfs(folders):
    count = 0

    for folder in no_data_folders:
        files = os.listdir(no_data_path + '/' + folder)

        if file[-4:] == '.pdf':
            count += 1

    return count


def partial_data_file_composition_is_correct(latest_actions_path, folder, required_file_types):
    folder_path = os.path.join(latest_actions_path,  folder)
    all_files = os.listdir(folder_path)
    pdf_files = [file for file in os.listdir(folder_path) if not file_is_a_word_document(file)]
    composition_is_correct = False

    if len(pdf_files) == len(all_files):
        composition_is_correct = required_data_file_types_are_present(folder, required_file_types)

    return composition_is_correct


def validate_folder_data(latest_actions_path, folder):
    failure_counts = []

    for file in [f for f in os.listdir(latest_actions_path + folder) if not f.startswith('.')]:
        file_path = os.path.join(latest_actions_path, folder, file)

        failure_count.append(validate_data_file(file_path))

    return functools.reduce(lambda a, b: a + b, failure_counts)


def file_is_a_word_document(file):
    is_word_doc = False

    if file.split('.')[-1] in ['docx', 'doc']:
        LOGGER.info('There is a non-pdf file: %s', file)
        is_word_doc = True

    return is_word_doc


def required_data_file_types_are_present(folder, required_file_types):
        folder_prefix = folder.rsplit('_', 5)[0]  # Example: NV_MD_SummaryList
        expected_file_types = required_file_types[folder_prefix]
        file_types = set([get_doc_type(file) for file in pdf_files])
        file_types_are_present = False

        if file_types == expected_file_types:
            file_types_are_present = True
        else:
            LOGGER.info('Expected file types %s for folder %s, but found only %s', expected_file_types, folder, file_types)


def validate_data_file(file_path, logger):
    failure_counts = FailureCounts()
    file_name = os.path.basename(file)
    file_type = get_doc_type(file_name)
    failure_counts = []

    failure_counts.append(validate_file_name(file_name, file_type, logger))

    failure_counts.append(validate_file_contents(file_path, file_type, logger))

    return functools.reduce(lambda a, b: a + b, failure_counts)


def get_doc_type(file_name) -> str:
    file_type = file_name.rsplit('.', 1)[0].rsplit('_', 1)[-1]

    # if there are multiple BO for same physician, need adjust to get 'BO'
    # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
    if re.match(r'#[0-9]', file_type) is not None:
        file_type = file_name.split('.')[0].rsplit('_', 2)[-2]

    return file_type


def validate_file_name(file_name, file_type, logger) -> FailureCounts:
    failure_counts = FailureCounts()

    if not file_name_is_valid(file_name, file_type):
        LOGGER.info('File name format is not right: %s', file_name)
        failure_counts.name_format = 1

        logger.info('%s, name_format', file_name)

    return failure_counts


def validate_file_contents(file_path, file_type, logger) -> FailureCounts:
    failure_counts = FailureCounts()

    if not file_contents_is_valid(file_path, file_type):
        LOGGER.info('%s file %s is not right', file_type, file_name)
        failure_counts.file_quality = 1

        logger.info('%s, file_quality - %s', file_name, "QA" if file_type == "QA" else "blank page")

    return failure_counts


def file_name_is_valid(file_name, file_type) -> bool:
    validator = FileValidatorFactory.create_validator(file_type)

    return validator.file_name_is_valid(file_name)


def file_contents_is_valid(file_name, file_type) -> bool:
    validator = FileValidatorFactory.create_validator(file_type)

    return validator.file_contents_is_valid(file_name)


# 3. check if can download to Udrive??
def check_in_udrive(path, UdrivePath) -> bool:
    return os.listdir(path) == os.listdir(UdrivePath)


if __name__ == '__main__':
    main()
