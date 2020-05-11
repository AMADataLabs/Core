""" Check the quality of disciplinary action data. """
import csv
from   dataclasses import dataclass
from   datetime import datetime
import glob
import json
import logging
import os
import re
from   time import strftime

from PyPDF2 import PdfFileReader

import settings

# CLEAN CODE NOTE: A proper logger allows you to easily adjust what level of logging is produced by the program.
#   The LOGGER is usually the only global variable/code I allow since per-function logging is too cluttered.
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class LogPaths:
    count: str = os.environ.get('COUNT_LOG')
    file: str = os.environ.get('FILE_LOG')


@dataclass
class FailureCounts:
    total: int = 0
    name_format: int = 0
    completeness: int = 0
    file_exists: int = 0
    file_quality: int = 0
    no_data_pdf: int = 0
    no_data_duplicate: int = 0


def main():
    # CLEAN CODE NOTE: Bring globals into main() and pass them to functions. This eliminates the risk of side effects
    #   while allowing the functions to be explicit about their parameters. Group parameters logically if needed.
    data_directory = os.environ.get('DATA_DIRECTORY')
    required_files = json.load(os.environ.get('REQUIRED_FILES'))
    log_paths = LogPaths()


    # CLEAN CODE NOTE: In general, names should reflect usage rather than implementation.
    # CLEAN CODE NOTE: DRY (Don't Repeat Yourself) principle:
    #   Just pass the mod date if you already retrieved it and you don't need the actual directory name for anything.
    # CLEAN CODE NOTE: multi-step logic at a lower level of abstraction should be placed in a function
    date_last_updated = modification_date(data_directory)

    # CLEAN CODE NOTE: Conditional blocks indicate logic at a lower-level of abstraction, so put the logic in functions.
    if new_data_available(date_last_updated):
        check_disciplinary_action_data_quality(data_directory, required_files, log_paths)
    else:
        LOGGER.info('No new folders uploaded. Last folder uploaded on %s.', date_last_updated)


def modification_date(path):
    mod_time_in_seconds = os.path.getmtime(path)

    mod_datetime = datetime.utcfromtimestamp(mod_time_in_seconds)

    return mod_datetime.date()


# CLEAN CODE NOTE: Summarize functions in the official "docstring"
def new_data_available(date_last_updated) -> bool:
    """ check if new data was uploaded to the directory of weekly result """
    today = datetime.datetime.utcnow()

    return date_last_updated == today


def check_disciplinary_action_data_quality(data_directory, required_files, log_paths):
    failure_counts = FailureCounts()
    # have new result updated, get path of new result and list of contents
    path, folders = get_latest_folder_path(data_directory)
    date = datetime.datetime.now().date()

    LOGGER.info('new folders uploaded: %s', path)

    # Step 0: check is new procurement or rebaseline folder:
    if check_new_pocurement(path):
        LOGGER.debug('This folder is new procurement')
        # Step 1: Validate Completeness:
        if not ValidateCompleteness(path):

            failure_counts.completeness += 1
        else:  # ValidateCompleteness is True
            if not check_files_exist(path):  # no_data folder is deleted in this function
                failure_counts.file_exists += 1
            else:  # check_files_exist is True
                LOGGER.info('folders are correct')
                LOGGER.debug('next step: check mandatory files contents in the folder')

                # Step 2: Validate Content Quality
                # remove no_data folder
                validfolders = [x for x in folders if x != 'no_data']
                for fold in validfolders:
                    for file in [f for f in os.listdir(path + '/' + fold) if not f.startswith('.')]:
                        fullpath = path + '/' + fold + '/' + file
                        # get the type of file: BO, SL, NL, QA, M (json)
                        type = get_doc_type(file)
                        # check name format:
                        if not check_file_name_format(file, type):
                            LOGGER.info('File Format is not right: %s as type %s', file, type)
                            failure_counts.name_format += 1
                            log_file_failure(log_paths.file,
                                             date,
                                             file,
                                             'name_format - file type')

                        # check csv file:
                        if type == 'QA':
                            if not check_qa_file(fullpath):
                                LOGGER.info('QA file %s is not right', file)
                                failure_counts.file_quality += 1
                                log_file_failure(log_paths.file,
                                                 date,
                                                 file,
                                                 'file_quality - QA')
                        # check board orders file:
                        elif type == 'BO' or type == 'SL' or type == 'NL':
                            if not check_bo_pdf(fullpath):
                                LOGGER.info('PDF file %s has blank page', file)
                                failure_counts.file_quality += 1
                                log_file_failure(log_paths.file,
                                                 date,
                                                 file,
                                                 'file_quality - blank page')


    else:
        LOGGER.debug('This folder is a re-baselined folder')
        #updatefolders = [f for f in os.listdir(data_directory + 'results_04_08_2020_09_10PM') if not f.startswith('.')]
        #updatefolders = [f for f in os.listdir(path) if not f.startswith('.')]
        validupdatefolders = [f for f in folders if f != 'no_data']
        for fold in validupdatefolders:
            for file in [f for f in os.listdir(path + fold) if not f.startswith('.')]:
                fullpath = path +'/' + fold + '/' + file
                # fullpath = '/Users/elaineyao/Desktop/QAtest/results_04_08_2020_09_10PM/' + fold + '/' + file
                type = get_doc_type(file)

                # check name format:
                if check_file_name_format(file, type):
                    LOGGER.debug('File format is right.')
                else:
                    LOGGER.info('File Format is not right: %s', file)
                    failure_counts.name_format += 1
                    log_file_failure(log_paths.file,
                                     date,
                                     file,
                                     'name_format')

                # check csv file:
                if type == 'QA':
                    # if not check_qa_file(fullpath):  # define the function to check qa csv file
                    if not check_qa_file(fullpath):
                        LOGGER.info('QA file %s is not right', file)
                        failure_counts.file_quality += 1
                        log_file_failure(log_paths.file,
                                         date,
                                         file,
                                         'file_quality - QA')
                # check board orders file:
                elif type == 'BO':
                    if not check_bo_pdf(fullpath):  # define the function to check board orders
                        LOGGER.info('BO file %s is not right', file)
                        failure_counts.file_quality += 1
                        log_file_failure(log_paths.file,
                                         date,
                                         file,
                                         'file_quality - BO')


with open(log_paths.count, 'a') as count_log_file:
    count_log_file.write(
        '\n{},{},{},{},{},{}, {}'.format(
            date, failcount, failure_counts.name_format, failure_counts.completeness, failure_counts.file_exists,
            failure_counts.file_quality, failure_counts.no_data_pdf, failure_counts.no_data_duplicate
        )
    )


def get_latest_folder_path(dir) -> list:
    # get latest result folder:
    list_of_files = glob.glob(f'{dir}/*')  # * means all if need specific format then *.csv
    latest_result = max(list_of_files, key=os.path.getctime)
    path = latest_result

    # folders under results: outside states + no_data
    folders = [f for f in os.listdir(latest_result) if not f.startswith('.')]
    return [path, folders]


# 1. check if it is new pocurement or re-baselined file
def check_new_pocurement(path) -> bool:
    if len(folders) + len(os.listdir(path + '/no_data')) == 70:
        return True
    return False


# 2. check Completeness:
def ValidateCompleteness(path) -> bool:
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
