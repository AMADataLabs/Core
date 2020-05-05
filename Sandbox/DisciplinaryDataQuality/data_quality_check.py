import os
import csv
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
import datetime
from time import strftime
import glob
import re

# TODO:
# 1. function check name format 3.5
# 2. get statistic data for weekly report and get PowerBI Dashboard

# Part 1: hard coding
# path of the directory of results
#directory = '/Users/elaineyao/Desktop/QAtest/'
directory = 'U:/Data Procurement & Disciplinary/JIRA Historical Documents/DISCP/'

count_log_path = 'U:/Source Files/Data Analytics/Data-Science/Data/Sanctions/DataQualityCheck/SanctionsQualityLog.csv'
file_log_path  = 'U:/Source Files/Data Analytics/Data-Science/Data/Sanctions/DataQualityCheck/SanctionsQualityFileLog.csv'

date = str(datetime.datetime.now().date())



# dictionary of each folder shouldhave what files:
doc_check_dic = {'SL&BO': ['CA_MD_SummaryList',
                           'FL_MD_SummaryList',
                           'FL_DO_SummaryList',
                           'OR_SummaryList',
                           'VA_SummaryList',
                           'IN_SummaryList',
                           'WV_MD_SummaryList',
                           'WV_DO_SummaryList',
                           'MO_SummaryList',
                           'MA_SummaryList',
                           'KY_SummaryList',
                           'DEA_SummaryList',
                           'MD_SummaryList',
                           'KS_SummaryList',
                           'AL_SummaryList',
                           'NY_SummaryList',
                           'AZ_DO_SummaryList',
                           'AZ_MD_SummaryList',
                           'CO_SummaryList',
                           'CT_SummaryList',
                           'DE_SummaryList',
                           'GA_SummaryList',
                           'HI_SummaryList',
                           'IA_SummaryList',
                           'ID_SummaryList',
                           'LA_SummaryList',
                           'MS_SummaryList',
                           'NC_SummaryList',
                           'NH_SummaryList',
                           'OH_SummaryList',
                           'RI_SummaryList',
                           'SD_SummaryList',
                           'WI_SummaryList',
                           'NV_DO_SummaryList',
                           'NV_MD_SummaryList',
                           'ME_MD_SummaryList',
                           'ME_DO_SummaryList',
                           'VT_MD_SummaryList',
                           'VT_DO_SummaryList',
                           'NJ_SummaryList',
                           'DC_SummaryList',
                           'ND_SummaryList',
                           'NM_MD_SummaryList',
                           'NM_DO_SummaryList',
                           'MN_SummaryList'],
                 'SL': ['CA_DO_SummaryList',
                        'AR_SummaryList',
                        'DHHS_SummaryList',
                        'AK_SummaryList',
                        'OK_DO_SummaryList',
                        'WY_SummaryList'],
                 'NL&BO': ['OR_Newsletter',
                           'MI_MD_Newsletter',
                           'MI_DO_Newsletter',
                           'CT_Newsletter',
                           'IL_Newsletter',
                           'OK_MD_Newsletter'],
                 'NL': ['CA_MD_Newsletter',
                        'WV_MD_Newsletter',
                        'WV_DO_Newsletter',
                        'KY_Newsletter',
                        'AL_Newsletter',
                        'PA_MD_Newsletter',
                        'PA_DO_Newsletter',
                        'UT_MD_Newsletter',
                        'UT_DO_Newsletter',
                        'TX_Newsletter',
                        'NV_MD_Newsletter']}


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
def check_file_nameformat(filename, type) -> bool:
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
        if keyvalue in doc_check_dic['SL&BO']:
            if set(filetype) == {'M', 'QA', 'SL', 'BO'}:
                return True
            else:
                print(f'only have {filetype}')
        elif keyvalue in doc_check_dic['SL']:
            if set(filetype) == {'M', 'QA', 'SL'}:
                return True
            else:
                print(f'only have {filetype}')
        elif keyvalue in doc_check_dic['NL&BO']:
            if set(filetype) == {'M', 'QA', 'NL', 'BO'}:
                return True
            else:
                print(f'only have {filetype}')
        elif keyvalue in doc_check_dic['NL']:
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


# Part 3: workflow:
# parameters for weekly report
failcount                   = 0
failcount_nameformat        = 0
failcount_completeness      = 0
failcount_fileexist         = 0
failcount_filequality       = 0
failcount_nodatapdf         = 0
failcount_nodataduplicate   = 0


def log_file_failure(file_log_path, date, file, failure_type):
    with open(file_log_path, 'a') as f:
        f.write(f'\n{date}, {file}, {failure_type}')


modtime_unix = os.path.getmtime(directory)

# Step 0: check if there is new result in directory, determine whether it is new procurement or re-baseline procurement
if not check_delivery(directory):
    # modtime_unix = os.path.getmtime(directory)
    moddate = datetime.datetime.utcfromtimestamp(modtime_unix).strftime('%Y-%m-%d')
    print(f'no new folders uploaded, latest folder uploaded at {moddate}')
else:
    # have new result updated, get path of new result and list of contents
    path, folders = get_latest_folder_path(directory)

    print(f'new folders uploaded: {path}')

    # Step 0: check is new procurement or rebaseline folder:
    if check_new_pocurement(path):
        print('This folder is new procurement')
        # Step 1: Validate Completeness:
        if not ValidateCompleteness(path):

            failcount_completeness += 1
        else:  # ValidateCompleteness is True
            if not check_files_exist(path):  # no_data folder is deleted in this function
                failcount_fileexist += 1
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
                        if not check_file_nameformat(file, type):
                            print(f'File Format is not right: {file} as type {type}')
                            failcount_nameformat += 1
                            log_file_failure(file_log_path=file_log_path,
                                             date=date,
                                             file=file,
                                             failure_type='nameformat - file type')

                        # check csv file:
                        if type == 'QA':
                            if not check_qa_file(fullpath):
                                print(f'QA file {file} is not right')
                                failcount_filequality += 1
                                log_file_failure(file_log_path=file_log_path,
                                                 date=date,
                                                 file=file,
                                                 failure_type='filequality - QA')
                        # check board orders file:
                        elif type == 'BO' or type == 'SL' or type == 'NL':
                            if not check_bo_pdf(fullpath):
                                print(f'PDF file {file} has blank page')
                                failcount_filequality += 1
                                log_file_failure(file_log_path=file_log_path,
                                                 date=date,
                                                 file=file,
                                                 failure_type='filequality - blank page')
                            #else:
                            #    print('')


    else:
        print('This folder is re-baselined folder')
        #updatefolders = [f for f in os.listdir(directory + 'results_04_08_2020_09_10PM') if not f.startswith('.')]
        #updatefolders = [f for f in os.listdir(path) if not f.startswith('.')]
        validupdatefolders = [f for f in folders if f != 'no_data']
        for fold in validupdatefolders:
            for file in [f for f in os.listdir(path + fold) if not f.startswith('.')]:
                fullpath = path +'/' + fold + '/' + file
                # fullpath = '/Users/elaineyao/Desktop/QAtest/results_04_08_2020_09_10PM/' + fold + '/' + file
                type = get_doc_type(file)

                # check name format:
                if check_file_nameformat(file, type):
                    print('File format is right.')
                else:
                    print(f'File Format is not right: {file}')
                    failcount_nameformat += 1
                    log_file_failure(file_log_path=file_log_path,
                                     date=date,
                                     file=file,
                                     failure_type='nameformat')

                # check csv file:
                if type == 'QA':
                    # if not check_qa_file(fullpath):  # define the function to check qa csv file
                    if not check_qa_file(fullpath):
                        print(f'QA file {file} is not right')
                        failcount_filequality += 1
                        log_file_failure(file_log_path=file_log_path,
                                         date=date,
                                         file=file,
                                         failure_type='filequality - QA')
                # check board orders file:
                elif type == 'BO':
                    if not check_bo_pdf(fullpath):  # define the function to check board orders
                        print(f'BO file {file} is not right')
                        failcount_filequality += 1
                        log_file_failure(file_log_path=file_log_path,
                                         date=date,
                                         file=file,
                                         failure_type='filequality - BO')


with open(count_log_path, 'a') as count_log_file:
    count_log_file.write('\n{},{},{},{},{},{}, {}'.format(date, failcount,
                                                          failcount_nameformat, failcount_completeness,
                                                          failcount_fileexist, failcount_filequality,
                                                          failcount_nodatapdf, failcount_nodataduplicate))

