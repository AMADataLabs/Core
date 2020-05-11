""" Check the quality of disciplinary action data. """
import csv
from   dataclasses import dataclass
import datetime
import glob
import json
import os
import re
from   time import strftime

from PyPDF2 import PdfFileReader

import settings


# path of the directory of results
DIRECTORY = os.environ.get('INPUT_DATA_DIRECTORY')

COUNT_LOG_PATH = os.environ.get('COUNT_LOG')
FILE_LOG_PATH = os.environ.get('FILE_LOG')

DATE = str(datetime.datetime.now().date())

DOC_CHECK_DICT = json.load(os.environ.get('TRACKED_FILES'))


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
    failure_counts = FailureCounts()

    modtime_unix = os.path.getmtime(DIRECTORY)

    # Step 0: check if there is new result in DIRECTORY, determine whether it is new procurement or re-baseline procurement
    if not check_delivery(DIRECTORY):
        # modtime_unix = os.path.getmtime(DIRECTORY)
        moddate = datetime.datetime.utcfromtimestamp(modtime_unix).strftime('%Y-%m-%d')
        print(f'no new folders uploaded, latest folder uploaded at {moddate}')
    else:
        # have new result updated, get path of new result and list of contents
        path, folders = get_latest_folder_path(DIRECTORY)

        print(f'new folders uploaded: {path}')

        # Step 0: check is new procurement or rebaseline folder:
        if check_new_pocurement(path):
            print('This folder is new procurement')
            # Step 1: Validate Completeness:
            if not ValidateCompleteness(path):

                failure_counts.completeness += 1
            else:  # ValidateCompleteness is True
                if not check_files_exist(path):  # no_data folder is deleted in this function
                    failure_counts.file_exists += 1
                else:  # check_files_exist is True
                    print('folders are correct, next step: check mandatory files contents in the folder')

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
                                print(f'File Format is not right: {file} as type {type}')
                                failure_counts.name_format += 1
                                log_file_failure(FILE_LOG_PATH=FILE_LOG_PATH,
                                                 date=date,
                                                 file=file,
                                                 failure_type='name_format - file type')

                            # check csv file:
                            if type == 'QA':
                                if not check_qa_file(fullpath):
                                    print(f'QA file {file} is not right')
                                    failure_counts.file_quality += 1
                                    log_file_failure(FILE_LOG_PATH=FILE_LOG_PATH,
                                                     date=date,
                                                     file=file,
                                                     failure_type='file_quality - QA')
                            # check board orders file:
                            elif type == 'BO' or type == 'SL' or type == 'NL':
                                if not check_bo_pdf(fullpath):
                                    print(f'PDF file {file} has blank page')
                                    failure_counts.file_quality += 1
                                    log_file_failure(FILE_LOG_PATH=FILE_LOG_PATH,
                                                     date=date,
                                                     file=file,
                                                     failure_type='file_quality - blank page')
                                #else:
                                #    print('')


        else:
            print('This folder is re-baselined folder')
            #updatefolders = [f for f in os.listdir(DIRECTORY + 'results_04_08_2020_09_10PM') if not f.startswith('.')]
            #updatefolders = [f for f in os.listdir(path) if not f.startswith('.')]
            validupdatefolders = [f for f in folders if f != 'no_data']
            for fold in validupdatefolders:
                for file in [f for f in os.listdir(path + fold) if not f.startswith('.')]:
                    fullpath = path +'/' + fold + '/' + file
                    # fullpath = '/Users/elaineyao/Desktop/QAtest/results_04_08_2020_09_10PM/' + fold + '/' + file
                    type = get_doc_type(file)

                    # check name format:
                    if check_file_name_format(file, type):
                        print('File format is right.')
                    else:
                        print(f'File Format is not right: {file}')
                        failure_counts.name_format += 1
                        log_file_failure(FILE_LOG_PATH=FILE_LOG_PATH,
                                         date=date,
                                         file=file,
                                         failure_type='name_format')

                    # check csv file:
                    if type == 'QA':
                        # if not check_qa_file(fullpath):  # define the function to check qa csv file
                        if not check_qa_file(fullpath):
                            print(f'QA file {file} is not right')
                            failure_counts.file_quality += 1
                            log_file_failure(FILE_LOG_PATH=FILE_LOG_PATH,
                                             date=date,
                                             file=file,
                                             failure_type='file_quality - QA')
                    # check board orders file:
                    elif type == 'BO':
                        if not check_bo_pdf(fullpath):  # define the function to check board orders
                            print(f'BO file {file} is not right')
                            failure_counts.file_quality += 1
                            log_file_failure(FILE_LOG_PATH=FILE_LOG_PATH,
                                             date=date,
                                             file=file,
                                             failure_type='file_quality - BO')


    with open(COUNT_LOG_PATH, 'a') as count_log_file:
        count_log_file.write(
            '\n{},{},{},{},{},{}, {}'.format(
                date, failcount, failure_counts.name_format, failure_counts.completeness, failure_counts.file_exists,
                failure_counts.file_quality, failure_counts.no_data_pdf, failure_counts.no_data_duplicate
            )
        )


# Part 2: User Define Functions
# 0. check if new result uploaded in the directory of weekly result
def check_delivery(direct) -> bool:
    # get most recent modification time:
    modtime_unix = os.path.getmtime(direct)
    moddate = datetime.datetime.utcfromtimestamp(modtime_unix).strftime('%Y-%m-%d')
    now = datetime.datetime.now()
    present_date = now.strftime('%Y-%m-%d')
    return moddate == present_date


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
        print('no pdf files in no_data folder. Good!')
        # b) check no same folder outside not data folder. # logic: whole folders in two layers == 69, loop to check the duplicate
        if len(folders) + len(nodatafolders) == 69:  # folders in total in and out no_data should be 69
            print('It seems the total number of folders is right, next step examine will be executed.')
            wholefolders = folders + nodatafolders
            noDupFolders = set(wholefolders)
            if len(wholefolders) == len(noDupFolders):
                print('there is no duplicate in the folder. Cool!')
                return True
            else:
                print('There is a duplicate folder in and out no_data folder.')
        else:
            print(f'folder total number is not right: {len(folders) + len(nodatafolders)}')


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
def check_files_exist(path) -> bool:
    validfolders = [x for x in folders if x != 'no_data']
    for f in validfolders:
        keyvalue = f.rsplit('_', 5)[0]
        # example: NV_MD_SummaryList

        filetype = []
        for i in os.listdir(path + '/' + f):
            # check if there is word file:
            if i.split('.')[-1] in ['docx', 'doc']:
                print(f'There is a non-pdf file: {i}')
                return False
            # get file type in each state folder:
            type = i.split('.')[0].rsplit('_', 1)[1]
            # if there are multiple BO for same physician, need adjust to get BO
            # Example: NY-Faizuddin_Shareef-03_11_2020_BO_#2.pdf
            if re.match(r'#[0-9]', type):
                type = i.split('.')[0].rsplit('_', 2)[-2]
            filetype.append(type)
        # check if all necessary files are in the folder:
        if keyvalue in DOC_CHECK_DICT['SL&BO']:
            if set(filetype) == {'M', 'QA', 'SL', 'BO'}:
                return True
            else:
                print(f'only have {filetype}')
        elif keyvalue in DOC_CHECK_DICT['SL']:
            if set(filetype) == {'M', 'QA', 'SL'}:
                return True
            else:
                print(f'only have {filetype}')
        elif keyvalue in DOC_CHECK_DICT['NL&BO']:
            if set(filetype) == {'M', 'QA', 'NL', 'BO'}:
                return True
            else:
                print(f'only have {filetype}')
        elif keyvalue in DOC_CHECK_DICT['NL']:
            if set(filetype) == {'M', 'QA', 'NL'}:
                return True
            else:
                print(f'only have {filetype}')


# 5. Validate Basic Content:
def check_qa_file(filepath) -> bool:
    with open(filepath, "r") as f:
        csvreader = csv.reader(f, delimiter=",")
        for row in csvreader:
            if row[1] in (None, ''):
                print(f'no value for {row[0]}')
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
            print(f'Page {i} of {filepath} is blank.')
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


def log_file_failure(FILE_LOG_PATH, date, file, failure_type):
    with open(FILE_LOG_PATH, 'a') as f:
        f.write(f'\n{date}, {file}, {failure_type}')


if __name__ == '__main__':
    main()
