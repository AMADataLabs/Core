"""CPT Table module"""

from collections import namedtuple
import boto3
import functools
import os
import pandas as pd
import tempfile


def get_cpt_files():
    s3 = boto3.client('s3')
    imported_file = []
    file_list = ['MEDU.txt', 'SHORTU.txt', 'LONGUF.txt', 'LONGULF.txt', 'LONGUT.txt', 'LONGULT.txt']
    FileDescriptor = namedtuple('description', 'name tab_separated')
    file_descriptors = [FileDescriptor('medium_description', False), FileDescriptor('short_description', False),
                        FileDescriptor('longuf_description', False), FileDescriptor('longulf_description', False),
                        FileDescriptor('longut_description', True), FileDescriptor('longult_description', True)]
    for file in file_list:
        with tempfile.NamedTemporaryFile(mode='r+') as temp:
            s3.download_file(os.environ['ingestion_bucket'], os.environ['s3_path'] + file, temp.name)
        imported_file.append(temp.name)

    return imported_file, file_descriptors


def parse_cpt_file(file_list, descriptions):
    cpt_df = []
    for files in file_list:
        checked_file = check_tab_delimited(files, file_list.index(files), descriptions)

        cpt_df.append(pd.read_fwf(checked_file, skiprows=32, names=['cpt_code', descriptions[file_list.index(files)]],
                                  colspecs=[(0, 5), (6, 66)]))

    return cpt_df


def check_tab_delimited(fname, index, descriptions):
    if not descriptions[index][0]:
        with open(fname, 'r') as f:
            data = f.read().replace('\t', '   ')
        with tempfile.TemporaryFile(mode='w') as temp:
            temp.write(data)
        return temp
    else:
        return fname


def cpt_to_csv(df, names):
    csv_file_names = []
    tempfile_holder = []

    for index, name in names:
        csv_file_names.append(index.split('_')[0]+'.csv')

    for name in csv_file_names:
        with tempfile.NamedTemporaryFile(mode='r+') as temp:
            df[csv_file_names.index(name)].to_csv(temp.name + '.csv', sep='\t')
            tempfile_holder.append(temp.name)

    merged_cpt_df = merge_tables(df)
    with tempfile.NamedTemporaryFile(mode='r+') as temp:
        merged_cpt_df.to_csv(temp.name + '.csv', sep='\t')
        tempfile_holder.append(temp.name)
        csv_file_names.append('cpt_table.csv')

    return tempfile_holder, csv_file_names


def merge_tables(df_list):
    df_merged = functools.reduce(lambda x, y: pd.merge(x, y, on='cpt_code'), df_list)
    return df_merged
