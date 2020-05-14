""" Check the quality of disciplinary action data. """
from   collections import Counter
import csv
from   dataclasses import dataclass
from   datetime import datetime
import functools
import glob
import json
import logging
import os
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

def main():
    data_base_path = os.environ.get('DATA_BASE_PATH')
    required_files = json.load(os.environ.get('REQUIRED_FILES'))
    # CLEAN CODE UPDATE: All setup dealing with dependencies should be done in the main function of the app.
    #
    #   This relates to the principle of Dependency Injection: all dependencies of a function should be
    #   "injected" into the function instead of the function searching for its dependencies outside of itself.
    #
    #   Since we can't have an "unmoved mover" scenario, the main function must be responsible for doing all of
    #   the injecting.
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
    current_date = datetime.datetime.now().date()

    LOGGER.info('New disciplinary action folders uploaded: %s', latest_actions_folder)

    if is_newly_procured_data(latest_actions_folder):
        LOGGER.debug('This folder is a newly-procured data folder')
        # CLEAN CODE NOTE: What does "validate" actually mean? What results from the validation?
        failure_counts = validate_newly_procured_data(latest_actions_folder)
    else:
        LOGGER.debug('This folder is a re-baselined data folder')
        # CLEAN CODE COMMENT: Delete any commented-out code before merging to master. Revision control got you covered!
        failure_counts = validate_rebaselined_data(latest_actions_folder)

    log_failure_counts(log_paths.count, failure_counts)


def get_latest_actions_folder(data_base_path) -> list:
    files = glob.glob(f'{data_base_path}/*')

    return max(files, key=os.path.getctime)


def is_newly_procured_data(latest_actions_folder, action_source_folders) -> bool:
    if len(action_source_folders) + len(folder_contents(latest_actions_folder + '/no_data')) == 69:
        return True
    return False


def validate_newly_procured_data(latest_actions_folder):
    failure_counts = None
    action_source_folders = folder_contents(latest_actions_folder)

    LOGGER.debug('This folder is new procurement')
    # CLEAN CODE NOTE: Ideally, writing clean code should obviate the need for procedural comments. Reserve comments
    #   for technical details that cannot be expressed easily otherwise.

    # CLEAN CODE NOTE: First, both the Be Consistent principle and the PEP style guide dictate that this function
    #   name should be in snake case.
    #
    #   Second, another ambigous "validate" function. In this case, its better to rename this with a boolean-returning name.
    if is_data_complete(latest_actions_folder):
        failure_counts = validate_complete_data(latest_actions_folder)
    else:
        failure_counts = FailureCounts(completeness=1)

    return failure_counts


def validate_rebaselined_data(latest_actions_folder):
    failure_counts = []
    action_source_folders = get_folder_contents(latest_actions_folder)

    # CLEAN CODE NOTE: Whatever language, use either snake case or camel case to break up words. Don't mash them togehter
    #   into an unreadable mess.
    #
    #   Also, consider putting potentially confusing code in a function to self-document.
    valid_update_folders = get_valid_update_folders(action_source_folders)
    # CLEAN CODE NOTE: Don't use misleading names, especially to save two characters of space.
    #
    #   A fold is a real thing and is different from a folder.
    #
    #   Also, "fold" is not a standard and unambiguous abbreviation for "folder".
    for folder in valid_update_folders:
        failure_counts.append(validate_update_folder(folder))

    return functools.reduce(lambda a, b: a + b, failure_counts)


def log_failure_counts(log_path, failure_counts, current_date):
    with open(log_path, 'a') as count_log_file:
        count_log_file.write(
            '\n{},{},{},{},{},{}, {}'.format(
                current_date, failcount, failure_counts.name_format, failure_counts.completeness,
                failure_counts.file_exists, failure_counts.file_quality, failure_counts.no_data_pdf,
                failure_counts.no_data_duplicate
            )
        )


# 2. check Completeness:
def is_data_complete(path) -> bool:
    # get folder and file list in nodata folder
    nodatapath = path + '/no_data'
    nodatafolders = [f for f in os.listdir(nodatapath) if not f.startswith('.')]
    all_files = []
    for entry in nodatafolders:
        files = os.listdir(nodatapath + '/' + entry)
        for i in files:
            all_files.append(i)
    # a) check if there is .pdf files
    count = 0
    for file in all_files:
        if file[-4:] == '.pdf':
            count += 1
    if count == 0:
        LOGGER.debug('no pdf files in no_data folder. Good!')
        # b) check no same folder outside not data folder. # logic: whole folders in two layers == 69, loop to check the duplicate
        if len(folders) + len(nodatafolders) == 69:  # folders in total in and out no_data should be 69
            LOGGER.info('It seems the total number of folders is correct.')
            LOGGER.debug('Next step, examine will be executed.')
            wholefolders = folders + nodatafolders
            noDupFolders = set(wholefolders)
            if len(wholefolders) == len(noDupFolders):
                LOGGER.debug('there is no duplicate in the folder. Cool!')
                return True
            else:
                LOGGER.info('There is a duplicate folder in and out no_data folder.')
        else:
            LOGGER.info('folder total number is not right: %d', len(folders) + len(nodatafolders))


def validate_complete_data(latest_actions_folder):
    failure_counts = FailureCounts()

    if not check_files_exist(latest_actions_folder):  # no_data folder is deleted in this function
        failure_counts.file_exists += 1
    else:  # check_files_exist is True
        LOGGER.info('Disciplinary action folders are correct')
        LOGGER.debug('next step: check mandatory files contents in the folder')

        # Step 2: Validate Content Quality
        # remove no_data folder
        validfolders = [x for x in action_source_folders if x != 'no_data']
        for folder in validfolders:
            for file in [f for f in os.listdir(latest_actions_folder + '/' + folder) if not f.startswith('.')]:
                fullpath = latest_actions_folder + '/' + folder + '/' + file
                # get the type of file: BO, SL, NL, QA, M (json)
                type = get_doc_type(file)
                # check name format:
                if not check_file_name_format(file, type):
                    LOGGER.info('File Format is not right: %s as type %s', file, type)
                    failure_counts.name_format += 1
                    log_file_failure(log_paths.file,
                                     current_date,
                                     file,
                                     'name_format - file type')

                # check csv file:
                if type == 'QA':
                    if not check_qa_file(fullpath):
                        LOGGER.info('QA file %s is not right', file)
                        failure_counts.file_quality += 1
                        log_file_failure(log_paths.file,
                                         current_date,
                                         file,
                                         'file_quality - QA')
                # check board orders file:
                elif type == 'BO' or type == 'SL' or type == 'NL':
                    if not check_bo_pdf(fullpath):
                        LOGGER.info('PDF file %s has blank page', file)
                        failure_counts.file_quality += 1
                        log_file_failure(log_paths.file,
                                         current_date,
                                         file,
                                         'file_quality - blank page')



def get_folder_contents(path) -> list:
    return [d for d in os.listdir(path) if not d.startswith('.')]


def get_valid_update_folders(action_source_folders):
    return [f for f in action_source_folders if f != 'no_data']


def validate_update_folder(folder)
    failure_counts = FailureCounts()

    for file in [f for f in os.listdir(latest_actions_folder + folder) if not f.startswith('.')]:
        fullpath = latest_actions_folder +'/' + folder + '/' + file
        # fullpath = '/Users/elaineyao/Desktop/QAtest/results_04_08_2020_09_10PM/' + folder + '/' + file
        type = get_doc_type(file)

        # check name format:
        if check_file_name_format(file, type):
            LOGGER.debug('File format is right.')
        else:
            LOGGER.info('File Format is not right: %s', file)
            failure_counts.name_format += 1
            log_file_failure(log_paths.file,
                             current_date,
                             file,
                             'name_format')

        # check csv file:
        if type == 'QA':
            # if not check_qa_file(fullpath):  # define the function to check qa csv file
            if not check_qa_file(fullpath):
                LOGGER.info('QA file %s is not right', file)
                failure_counts.file_quality += 1
                log_file_failure(log_paths.file,
                                 current_date,
                                 file,
                                 'file_quality - QA')
        # check board orders file:
        elif type == 'BO':
            if not check_bo_pdf(fullpath):  # define the function to check board orders
                LOGGER.info('BO file %s is not right', file)
                failure_counts.file_quality += 1
                log_file_failure(log_paths.file,
                                 current_date,
                                 file,
                                 'file_quality - BO')


# 3. check if can download to Udrive??
def check_in_udrive(path, UdrivePath) -> bool:
    return os.listdir(path) == os.listdir(UdrivePath)


# 3.5 check file format: Agency_Date-Time_SL/NL.pdf, Agency-Physician_Name-Date_Time_BO.pdf
def check_file_name_format(filename, type) -> bool:
    if type == 'SL':
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_SL.pdf'
        if re.match(pattern, filename) is not None:
            return True
        else:
            if filename.split('-')[0] == 'DHHS':
                pattern = r'DHHS-\S*_SL.pdf'
                if re.match(pattern, filename) is not None:
                    return True
    elif type == 'NL':
        pattern = r'[A-Z_]*_[0-9]*-[0-9]*-[0-9]*_NL.pdf'
        if re.match(pattern, filename) is not None:
            return True
    elif type == 'BO':
        # Exception: DHHS-2003REIN_BO.pdf
        if filename.split('-')[0] == 'DHHS':
            pattern = r'DHHS-\S*_BO.pdf'
            if re.match(pattern, filename) is not None:
                return True
        pattern = r'\S*-[0-9]*_[0-9]*_[0-9]*_BO.pdf'
        if re.match(pattern, filename) is not None:
            return True
        else:
            pattern = r'\S*-[0-9]*_[0-9]*_[0-9]*_BO_#[0-9].pdf'
            if re.match(pattern, filename) is not None:
                return True
    elif type == 'QA' or type == 'M':
        return True
    else:
        return False


# 4. check if mandatory files exits in each folder
def check_files_exist(path, required_files) -> bool:
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
            type = i.split('.')[0].rsplit('_', 1)[1]
            # if there are multiple BO for same physician, need adjust to get BO
            # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
            if re.match(r'#[0-9]', type):
                type = i.split('.')[0].rsplit('_', 2)[-2]
            filetype.append(type)
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


# 5. Validate Basic Content:
def check_qa_file(filepath) -> bool:
    with open(filepath, "r") as f:
        csvreader = csv.reader(f, delimiter=",")
        for row in csvreader:
            if row[1] in (None, ''):
                LOGGER.info('no value for %d', row[0])
                return False
            else:
                continue
    return True


def check_bo_pdf(filepath) -> bool:
    pdfObj = PdfFileReader(open(filepath, 'rb'))
    pagenum = pdfObj.getNumPages()
    for i in range(pagenum):
        # Page is blank or not
        if pdfObj.getPage(i).getContents() is None:
            LOGGER.info('Page %d of %s is blank.', i, filepath)
            return False
    return True
    # Page is distorted or not: TODO.


def get_doc_type(filename) -> str:
    type = filename.rsplit('.', 1)[0].rsplit('_', 1)[-1]
    # if there are multiple BO for same physician, need adjust to get 'BO'
    # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
    if re.match(r'#[0-9]', type) is not None:
        type = filename.split('.')[0].rsplit('_', 2)[-2]
        return type
    return type


def log_file_failure(log_path, date, file, failure_type):
    with open(log_path, 'a') as f:
        f.write(f'\n{date}, {file}, {failure_type}')


if __name__ == '__main__':
    main()
