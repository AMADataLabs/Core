""" Check the quality of disciplinary action data. """
from   abc import ABC, abstractmethod
from   collections import Counter
import csv
from   dataclasses import dataclass
from   datetime import datetime
import functools
import glob
import json
import logging
import os
import pandas
import re
from   time import strftime

from PyPDF2 import PdfFileReader

import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class LogPaths:
    count: str
    file: str


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
    def file_name_is_valid(self, filename):
        pass

    @abstractmethod
    def file_contents_is_valid(self, filename):
        pass


class IgnoreNameFileValidatorMixin:
    def file_name_is_valid(self, filename):
        return True


class IgnoreContentsFileValidatorMixin:
    def file_contents_is_valid(self, filename):
        return True


class PDFFileContentsValidatorMixin:
    def file_contents_is_valid(self, filename):
        # TODO: Page is distorted or not
        is_valid = True

        with file in open(filename, 'rb'):
            pdf = PdfFileReader(open(filename, 'rb'))

        for page_number, page in enumerate(pdf.pages):
            if _page_is_blank(page):
                LOGGER.info('Page %d of %s is blank.', page_number, filename)
                is_valid = False

        return is_valid


class SLFileValidator(PDFFileContentsValidatorMixin, FileValidator);
    def file_name_is_valid(self, filename):
        is_valid = False
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_SL.pdf'

        if re.match(pattern, filename) is not None:
            is_valid = True
        else:
            if filename.split('-')[0] == 'DHHS':
                pattern = r'DHHS-\S*_SL.pdf'
                if re.match(pattern, filename) is not None:
                    is_valid = True


class NLFileValidator(PDFFileContentsValidatorMixin, FileValidator);
    def file_name_is_valid(self, filename):
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_NL.pdf'

        if re.match(pattern, filename) is not None:
            return True


class BOFileValidator(PDFFileContentsValidatorMixin, FileValidator):
    def file_name_is_valid(self, filename):
        is_valid = False

        if filename.split('-')[0] == 'DHHS':
            pattern = r'DHHS-\S*_BO.pdf'
            if re.match(pattern, filename) is not None:
                is_valid = True

        pattern = r'\S*-[0-9]*_[0-9]*_[0-9]*_BO.pdf'
        if re.match(pattern, filename) is not None:
            is_valid = True
        else:
            pattern = r'\S*-[0-9]*_[0-9]*_[0-9]*_BO_#[0-9].pdf'
            if re.match(pattern, filename) is not None:
                is_valid = True

    @classmethod
    def _page_is_blank(cls, page):
        return page.getContents() is None


class QAFileValidator(IgnoreNameFileValidatorMixin, PDFFileContentsValidatorMixin, FileValidator):
    def file_contents_is_valid(self, filename):
        data = pandas.read_csv(filename)

        return np.all(pandas.isnull(data))


class MFileValidator(IgnoreNameFileValidatorMixin, IgnoreContentsFileValidatorMixin, FileValidator):
    pass


class FileValidatorFactory():
    VALIDATORS = dict(
        SL=SLFileValidator,
        NL=FileValidator,
        BO=BOFileValidator,
        QA=DefaultFileValidator,
        M=DefaultFileValidator,
    )

    @classmethod
    def create_validator(cls, file_type):
        if file_type not in VALIDATOR_TABLE:
            raise ValueError(f"File type '{file_type}' is not supported.")

        return VALIDATORS[file_type]()


def main():
    data_base_path = os.environ.get('DATA_BASE_PATH')
    required_files = json.load(os.environ.get('REQUIRED_FILES'))
    log_paths = LogPaths(
        count=os.environ.get('COUNT_LOG'),
        file=os.environ.get('FILE_LOG')
    )
    date_last_updated = modification_date(data_base_path)

    if new_data_available(date_last_updated):
        check_disciplinary_action_data_quality(data_base_path, required_files, log_paths)
    else:
        LOGGER.info('No new folders uploaded. Last folder uploaded on %s.', date_last_updated)


def modification_date(path):
    mod_time_in_seconds = os.path.getmtime(path)

    mod_datetime = datetime.utcfromtimestamp(mod_time_in_seconds)

    return mod_datetime.date()


def new_data_available(date_last_updated) -> bool:
    """ check if new data was uploaded to the folder of weekly results """
    today = datetime.datetime.utcnow()

    return date_last_updated == today


def check_disciplinary_action_data_quality(data_base_path, required_files, log_paths):
    failure_counts = None
    latest_actions_folder = get_latest_actions_folder(data_base_path)
    action_source_folders = get_folder_contents(latest_actions_folder)
    no_data_folders = get_folder_contents(no_data_path)
    current_date = datetime.datetime.now().date()


    LOGGER.info('New disciplinary action folders uploaded: %s', latest_actions_folder)

    if is_newly_procured_data(no_data_folders, action_source_folders):
        LOGGER.debug('This folder is a newly-procured data folder')
        failure_counts = validate_newly_procured_data(latest_actions_folder, action_source_folders, no_data_folders)
    else:
        LOGGER.debug('This folder is a re-baselined data folder')
        failure_counts = validate_rebaselined_data(latest_actions_folder, action_source_folders)

    log_failure_counts(log_paths.count, failure_counts)


def get_latest_actions_folder(data_base_path) -> list:
    files = glob.glob(f'{data_base_path}/*')

    return max(files, key=os.path.getctime)


def get_folder_contents(path) -> list:
    return [d for d in os.listdir(path) if not d.startswith('.')]


def is_newly_procured_data(no_data_folders, action_source_folders) -> bool:
    if len(action_source_folders) + len(no_data_folders) == 69:
        return True
    return False


def validate_newly_procured_data(latest_actions_folder, action_source_folders, no_data_folders) -> FailureCounts:
    failure_counts = None
    no_data_path = latest_actions_folder + '/no_data'

    LOGGER.debug('This folder is a new procurement')

    if data_is_complete(action_source_folders, no_data_folders):
        failure_counts = validate_data(latest_actions_folder, action_source_folders)
    else:
        failure_counts = FailureCounts(completeness=1)

    return failure_counts


def validate_rebaselined_data(latest_actions_folder, action_source_folders) -> FailureCounts:
    return validate_data(latest_actions_folder, action_source_folders)


def log_failure_counts(log_path, failure_counts, current_date):
    with open(log_path, 'a') as count_log_file:
        count_log_file.write(
            '\n{},{},{},{},{},{}, {}'.format(
                current_date, failcount, failure_counts.name_format, failure_counts.completeness,
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


def validate_data(latest_actions_folder, action_source_folders):
    failure_counts = []

    if mandatory_data_files_exist(latest_actions_folder):  # no_data folder is deleted in this function
        LOGGER.info('Disciplinary action folders are correct')
        LOGGER.debug('next step: check mandatory files contents in the folder')

        failure_counts = validate_data_files(latest_actions_folder, action_source_folders)
    else:
        failure_counts.append(FailureCounts(file_exists=1))


def get_valid_update_folders(action_source_folders):
    return [f for f in action_source_folders if f != 'no_data']


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
        are_unique True
    else:
        LOGGER.info('Duplicate folder found in no_data folder.')

    return are_unique


# 4. check if mandatory files exits in each folder
def mandatory_data_files_exist(path, required_files) -> bool:
    validfolders = [x for x in folders if x != 'no_data']
    for f in validfolders:
        keyvalue = f.rsplit('_', 5)[0]
        # example: NV_MD_SummaryList

        filetype = []
        for i in os.listdir(path + '/' + f):
            # check if there is word file:
            if i.split('.')[-1] in ['docx', 'doc']:
                LOGGER.info('There is a non-pdf file: %s', i)
                return False

            # get file type in each state folder:
            file_type = i.split('.')[0].rsplit('_', 1)[1]
            # if there are multiple BO for same physician, need adjust to get BO
            # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
            if re.match(r'#[0-9]', file_type):
                file_type = i.split('.')[0].rsplit('_', 2)[-2]
            filetype.append(file_type)


        # check if all necessary files are in the folder:
        if keyvalue in expected_files['SL&BO']:
            if set(filetype) == {'M', 'QA', 'SL', 'BO'}:
                return True
            else:
                LOGGER.info('only have %s', filetype)
        elif keyvalue in expected_files['SL']:
            if set(filetype) == {'M', 'QA', 'SL'}:
                return True
            else:
                LOGGER.info('only have %s', filetype)
        elif keyvalue in expected_files['NL&BO']:
            if set(filetype) == {'M', 'QA', 'NL', 'BO'}:
                return True
            else:
                LOGGER.info('only have %s', filetype)
        elif keyvalue in expected_files['NL']:
            if set(filetype) == {'M', 'QA', 'NL'}:
                return True
            else:
                LOGGER.info('only have %s', filetype)


def validate_data_files(latest_actions_folder, action_source_folders):
    for folder in get_valid_update_folders(action_source_folders):
        failure_counts = validate_folder_data(latest_actions_folder, folder)

    return functools.reduce(lambda a, b: a + b, failure_counts)


def validate_folder_data(latest_actions_folder, folder)
    failure_counts = []

    for file in [f for f in os.listdir(latest_actions_folder + folder) if not f.startswith('.')]:
        file_path = os.path.join(latest_actions_folder, folder, file)

        failure_count.append(validate_data_file())

    return functools.reduce(lambda a, b: a + b, failure_counts)


def validate_data_file(file_path):
    failure_counts = FailureCounts()
    file_name = os.path.basename(file)
    file_type = get_doc_type(file_name)

    # check name format:
    if not file_name_is_valid(file_name, file_type):
        LOGGER.info('File name format is not right: %s', file_name)
        failure_counts.name_format = 1
        log_file_failure(log_paths.file,
                         current_date,
                         file_name,
                         'name_format')

    if not file_contents_is_valid(file_path, file_type):
        LOGGER.info('%s file %s is not right', file_type, file_name)
        failure_counts.file_quality = 1
        log_file_failure(log_paths.file,
                         current_date,
                         file_name,
                         f'file_quality - {file_type or "blank page" if file_type != "QA"}')

    return failure_counts


def get_doc_type(filename) -> str:
    type = filename.rsplit('.', 1)[0].rsplit('_', 1)[-1]
    # if there are multiple BO for same physician, need adjust to get 'BO'
    # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
    if re.match(r'#[0-9]', type) is not None:
        type = filename.split('.')[0].rsplit('_', 2)[-2]
        return type
    return type


def file_name_is_valid(filename, file_type) -> bool:
    validator = FileValidatorFactory.create_validator(file_type)

    return validator.file_name_is_valid(filename)


def file_contents_is_valid(filename, file_type) -> bool:
    validator = FileValidatorFactory.create_validator(file_type)

    return validator.file_contents_is_valid(filename)


def count_pdfs(folders):
    count = 0

    for folder in no_data_folders:
        files = os.listdir(no_data_path + '/' + folder)

        if file[-4:] == '.pdf':
            count += 1

    return count


# 3. check if can download to Udrive??
def check_in_udrive(path, UdrivePath) -> bool:
    return os.listdir(path) == os.listdir(UdrivePath)


def log_file_failure(log_path, date, file, failure_type):
    with open(log_path, 'a') as f:
        f.write(f'\n{date}, {file}, {failure_type}')


if __name__ == '__main__':
    main()
