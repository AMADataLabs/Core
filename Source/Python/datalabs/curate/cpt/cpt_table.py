import pandas as pd
import os
import functools
import boto3

def parse_cpt_txt(file_list, t_description):
    cpt_df = []

    for l in file_list:
        if 't' in t_description[file_list.index(l)].split('_')[0]:

            # replace tabs with spaces in txt file
            fin = open(l, 'r')
            data = fin.read().replace('\t', '   ')
            fin.close()

            fout = open('new.txt', 'w')
            fout.write(data)
            fout.close()

            # convert data from text to dataframe and table format
            cpt_df.append(pd.read_fwf(l, skiprows=32, names=['cpt_code', t_description[file_list.index(l)]],
                                      colspecs=[(0, 5), (6, 66)]))
            os.remove("new.txt")
        else:
            cpt_df.append(pd.read_fwf(l, skiprows=32, names=['cpt_code', t_description[file_list.index(l)]],
                                      colspecs=[(0, 5), (6, 66)]))

    df_to_csv(cpt_df, t_description)


def df_to_csv(df, names):
    # create csv file from dataframe
    i = 0
    while i < len(names):
        file_name = names[i].split('_')
        df[i].to_csv(file_name[0] + '.csv')
        i = i + 1
    merge_tables(df)


def merge_tables(df_list):
    df_merged = functools.reduce(lambda x, y: pd.merge(x, y, on='cpt_code'), df_list)
    df_merged.to_csv('cpt_table.csv', sep='\t')
    s3 = boto3.client('s3')
    try:
        s3.upload_file('cpt_table.csv', 'ama-hsg-datalabs-datalake-ingestion-sandbox', 'cpt_table.csv')
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False


def get_s3_files():
    s3 = boto3.client('s3')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/MEDU.txt', 'medium.txt')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/SHORTU.txt', 'short.txt')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/LONGUF.txt', 'longf.txt')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/LONGULF.txt',
                     'longfl.txt')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/LONGUT.txt', 'longt.txt')
    s3.download_file('ama-hsg-datalabs-datalake-ingestion-sandbox', 'AMA/CPT/20200131/standard/LONGULT.txt',
                     'longtl.txt')
    file_list = ['medium.txt', 'short.txt', 'longf.txt', 'longfl.txt', 'longt.txt', 'longtl.txt']
    file_descriptions = ['medium_description', 'short_description', 'longuf_description', 'longulf_description',
                         'longut_description', 'longult_description']
    parse_cpt_txt(file_list, file_descriptions)
    for f in file_list:
        os.remove(f)


def main():
    get_s3_files()

if __name__ == "__main__":
    main()

