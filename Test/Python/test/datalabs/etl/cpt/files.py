"""
Local test for searching the processed data S3 bucket for the most recent (current)
and next most recent (prior) release distribution zip files
local directoy list:
xxx/data/cpt/files//20220830
xxx/data/cpt/files//20220829
xxx/data/cpt/files//20220826
xxx/data/cpt/files//20220825
xxx/data/cpt/files//20220824
"""
import glob
import os
import  datalabs.etl.cpt.files as s3
import mock

# pylint: disable=redefined-outer-name, disable=C0103
# local directoy list"
drive_name = "OneDrive - American Medical Association"
directory = "/mnt/c/Users/rsun/"+drive_name+"/data/cpt/files"
directory_empty = "/mnt/c/Users/rsun/"+drive_name+"/data/cpt/files1"

# pylint: disable=redefined-outer-name, protected-access, disable=C0103
#mock the results of the directory listing
def get_two_latest_path(directory) -> list:
    with mock.patch('boto3.client'):
        list_of_files = glob.glob(f'{directory}/*')
        latest_res, second_latest_res = '', ''

        if len(list_of_files) >= 2:
            latest_res = max(list_of_files, key=os.path.getctime)
            list_of_files_noMax = [i for i in list_of_files if i != latest_res]
            second_latest_res = max(list_of_files_noMax)
            path = [latest_res, second_latest_res]
        elif len(list_of_files) == 1:
            path = [latest_res, None]
        elif len(list_of_files) == 0:
            path = [None, None]

    return [list_of_files, path]

# pylint: disable=redefined-outer-name, protected-access, disable=C0103
def _get_local_files(task, directory):
    base_path = get_two_latest_path(directory)[1]
    current_base_path = base_path[0]
    prior_base_path = base_path[1]
    files, current_files, prior_files = [], [], []

    if task._parameters.link_files_zip is not None:
        files = task._parameters.link_files_zip.split(',')
    else:
        raise ValueError('"files" parameter must contain the list of files to extract.')

    if (current_base_path is not None) and (prior_base_path is not None):
        current_files = ['/'.join((current_base_path, file.strip())) for file in files]
        prior_files = ['/'.join((prior_base_path, file.strip())) for file in files]
        files = current_files + prior_files
    elif current_base_path is not None:
        files = ['/'.join((current_base_path, file.strip())) for file in files]
    else:
        files = []

    return files

# pylint: disable=redefined-outer-name, protected-access, disable=C0103
def ReleaseFilesListExtractorTaskTests(parameters):
    with mock.patch('boto3.client'):
        parameters['base_path'] = directory
        parameters['link_files_zip'] = 'files_test.zip'
        parameters['execution_time'] = '20220830'

        task = s3.ReleaseFilesListExtractorTask(parameters)
        result_files = _get_local_files(task, directory)
        #assert that correct run directories are chosen and correct zip file paths are generated
        list_of_dir = get_two_latest_path(directory)[0]
        current_files = result_files[0]
        prior_files =  result_files[1]
        assert len(list_of_dir) == 5
        assert len(result_files) == 2

        drive_name = "OneDrive - American Medical Association"
        assert current_files =='/mnt/c/Users/rsun/'+drive_name+'/data/cpt/files/20220830/files_test.zip'
        assert prior_files =='/mnt/c/Users/rsun/'+drive_name+'/data/cpt/files/20220829/files_test.zip'

        # empty directory
        list_of_files_empty = get_two_latest_path(directory_empty)[0]
        assert len(list_of_files_empty) == 0
        result_empty = _get_local_files(task, directory_empty)
        # empty directory with zip files
        assert len(result_empty) == 0

ReleaseFilesListExtractorTaskTests(parameters = {})
