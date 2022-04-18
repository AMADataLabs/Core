2# Kari Palmier    Created 8/8/19
# Kari Palmier    Updated to filter known bad by if they are in current PPD
#
#############################################################################
import argparse
import os
import sys
import tkinter as tk
from tkinter import filedialog
import datetime

import pandas as pd

import settings
from create_batch_loads import create_phone_delete, combine_batches
from select_files import select_files
from combine_data import combine_data

import datalabs.curate.dataframe  # pylint: disable=unused-import
import datalabs.util.datetime as dt


def main(args):
    report_cols = ['WSLIVE_FILE_DT', 'OFFICE_TELEPHONE', 'OFFICE_PHONE_VERIFIED_UPDATED', 'COMMENTS', 'WSLIVE_SOURCE', 
                   'PHONE_STATUS', 'PHYSICIAN_FIRST_NAME', 'PHYSICIAN_MIDDLE_NAME', 'PHYSICIAN_LAST_NAME']

    root = tk.Tk()
    root.withdraw()

    mf_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\Analysis\\'
    vt_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Vertical_Trail\Analysis\\'
    iq_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IQVIA\Analysis\\'
    sym_anlys_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Symphony\Analysis\\'


    init_wslive_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\'
    wslive_results_file = filedialog.askopenfilename(initialdir=init_wslive_dir,
                                                     title="Choose WSLive file with results encoded...")

    init_ppd_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\PPD\\'
    ppd_file = filedialog.askopenfilename(initialdir = init_ppd_dir,
                                             title = "Choose latest PPD CSV file...")

    init_batch_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\IT_BatchLoads\\Humach_Surveys\\'
    batch_out_dir = filedialog.askdirectory(initialdir = init_batch_dir,
                                             title = "Choose directory to save removal batch file output...")
    batch_out_dir = batch_out_dir.replace("/", "\\")
    batch_out_dir += "\\"

    current_time = datetime.datetime.now()
    start_time_str = current_time.strftime("%Y-%m-%d")

    start_date, end_date, date_range_str = dt.date_range(args['start-date'], args['end-date'])

    print('\n\n')
    smpl_str = input('Do you want to match results to samples sent? ([y]/n): ')
    smpl_str = smpl_str.lower()
    if smpl_str.find('n') < 0:
        smpl_str = 'y'
        
    sample_paths = []
    if smpl_str.find('n') < 0:
        init_sample_dir = 'U:\\Source Files\\Data Analytics\\Data-Science\\Data\\Survey_Samples\\'
        sample_paths = select_files(init_sample_dir, 'Select sample file(s) sent corresponding to results')


    print('\n\n')
    print('Source Codes:')
    print('MF = Masterfile')
    print('MR = Masterfile Random')
    print('MA = Masterfile Risky W Email')
    print('MB = Masterfile Risky No Email')
    print('I = IQVIA')
    print('S = Symphony')
    print('VT = Vertical Trail')
    source_str = input('Enter the source codes to analyze (comma sep, default = all): ')
    source_str = source_str.upper()
    source_lst = source_str.split(',')
    for i in range(len(source_lst)):
        source_lst[i] = source_lst[i].strip()
    if len(set(source_lst).intersection(set(['MF', 'MR', 'MA', 'MB', 'I', 'S', 'VT']))) != len(source_lst):
        survey_sources = [['C', 'Z'], 'CR', 'CA', 'CB', 'Q', 'S', 'VT']
        source_names = ['MF', 'MF Random', 'MF Risky W Email', 'MF Risky No Email', 'IQVIA', 
                        'Symphony', 'Vertical Trail']
    else:  
        survey_sources = []
        source_names = []
        for i in range(len(source_lst)):
            temp_src = source_lst[i]
        
            if temp_src == 'MF':
                survey_sources.append(['C', 'Z'])
                source_names.append(source_str)
            elif temp_src == 'I':
                survey_sources.append('Q')
                source_names.append('IQVIA')
            elif temp_src == 'MR':
                survey_sources.append('CR')
                source_names.append('MF Random')
            elif temp_src == 'MA':
                survey_sources.append('CA')
                source_names.append('MF Risky W Email')
            elif temp_src == 'MB':
                survey_sources.append('CB')
                source_names.append('MF Risky No Email')
            elif temp_src == 'S':
                source_names.append('Symphony')
            elif temp_src == 'VT':
                survey_sources.append(source_str)
                source_names.append('Vertical Trail')
            
    count_end_name = '_WSLive_Result_Counts.xlsx'
    kb_end_name = '_WSLive_KnownBad_Counts.xlsx'
    report_end_name = '_WSLive_Report_Data.csv'

    old_stdout = sys.stdout
    log_filename = mf_anlys_dir + date_range_str + '_WSLive_Analysis_Log.txt'
    log_file = open(log_filename, "w")
    sys.stdout = log_file

    # Read in samples sent
    if len(sample_paths) > 0:
        sample_df = combine_data(sample_paths, None, 0)
        sample_df = sample_df.datalabs.rename_in_upper_case()

    # Read in PPD data
    ppd_df = pd.read_csv(ppd_file, delimiter = ",", index_col = None, header = 0, dtype = 'object')
    ppd_df = ppd_df.datalabs.rename_in_upper_case()

    # Read in wslive data
    wslive_results_df = pd.read_csv(wslive_results_file, delimiter = ",", index_col = None, header = 0, dtype = str)
    wslive_results_df = wslive_results_df.datalabs.rename_in_upper_case()

    # Get data for date range specified
    wslive_results_df['WSLIVE_FILE_DT'] = pd.to_datetime(wslive_results_df['WSLIVE_FILE_DT'])
    wslive_res_date_df = wslive_results_df[(wslive_results_df['WSLIVE_FILE_DT'] >= start_date) & \
                                      (wslive_results_df['WSLIVE_FILE_DT'] <= end_date)]


    # Join results with sample sent on ME
    if len(sample_paths) > 0:
        wslive_res_smpl_df = wslive_res_date_df.merge(sample_df, how = 'inner', left_on = 'PHYSICIAN_ME_NUMBER',
                                                     right_on = 'ME')
        sample_cols = sample_df.columns.values
        rename_dict = {}
        for name in sample_cols:
            rename_dict[name] = 'INIT_' +  name
        wslive_res_smpl_df = wslive_res_smpl_df.rename(columns = rename_dict)
    else:
        wslive_res_smpl_df = wslive_res_date_df

                
    # Loop over source types and compile results for each
    status_types = ['PHONE_STATUS', 'ADDR_STATUS', 'FAX_STATUS', 'PE_STATUS', 'SPEC_STATUS', 'NEW_METRIC']
    kb_uniq_comb_batch_df = pd.DataFrame()
    for i in range(len(survey_sources)):
        
        source_code = survey_sources[i]
        source_name = source_names[i]
        
        if source_name.find('MF') >= 0:
            anlys_out_dir = mf_anlys_dir
        elif source_code == 'Q':
            anlys_out_dir = iq_anlys_dir
        elif source_code == 'S':
            anlys_out_dir = sym_anlys_dir
        elif source_code == 'VT':
            anlys_out_dir = vt_anlys_dir
                    
        anlys_base_name = anlys_out_dir + date_range_str + '_'
        support_dir = anlys_out_dir + 'Support\\'
        if not os.path.exists(support_dir):
            os.mkdir(support_dir)

        # If source type for MF is a list so need to treat differently
        if type(source_code).__name__ == 'list':
            wslive_source_df = wslive_res_smpl_df[wslive_res_smpl_df['SOURCE'].isin(source_code)]
        else:
            wslive_source_df = wslive_res_smpl_df[wslive_res_smpl_df['SOURCE'] == source_code]
            
        if wslive_source_df.shape[0] == 0:
            continue
            

        # Report analysis summaries for each phone entry type
        print('\n')
        print('--------------------------------------------------------------')
        print(source_name)
        print('--------------------------------------------------------------')
        print('Number of entries for {}: {}'.format(source_name, wslive_source_df.shape[0]))
        print('Number of phone Confirmed for {}: {}'.format(source_name, wslive_source_df[wslive_source_df['PHONE_STATUS'] == \
              'Confirmed'].shape[0]))
        print('Number of phone Inconclusive for {}: {}'.format(source_name, wslive_source_df[wslive_source_df['PHONE_STATUS'] == \
              'Inconclusive'].shape[0]))
        print('Number of phone Known Bad for {}: {}'.format(source_name, wslive_source_df[wslive_source_df['PHONE_STATUS'] == \
              'Known Bad'].shape[0]))
        print('Number of phone No Contact for {}: {}'.format(source_name, wslive_source_df[wslive_source_df['PHONE_STATUS'] == \
              'No Contact'].shape[0]))
        print('Number of phone Updated for {}: {}'.format(source_name, wslive_source_df[wslive_source_df['PHONE_STATUS'] == \
              'Updated'].shape[0]))
            
        anlys_out_file = anlys_base_name + source_name + count_end_name
        kb_out_file = anlys_base_name + source_name + kb_end_name
        res_writer = pd.ExcelWriter(anlys_out_file, engine = 'xlsxwriter')
        kb_writer = pd.ExcelWriter(kb_out_file, engine = 'xlsxwriter')

        for status in status_types:
            
            if source_name.find('MF') < 0 and status in ['PE_STATUS', 'SPEC_STATUS', 'NEW_METRIC']:
                continue
            
            # Generate dataframes with counts of each result (Confirmed, Updated, etc) per entry type
            month_cnt, all_cnt, kb_month_cnt, kb_all_cnt = get_type_counts(wslive_source_df, status)
            
            if status == 'NEW_METRIC':            
                status_start = 'total'
            else:
                under_ndx = status.find('_')
                status_start = status[:under_ndx].lower()
                        
            month_count_sheet = status_start + '_count_monthly'
            month_cnt.to_excel(res_writer, sheet_name = month_count_sheet, index = False, header = True)
        
            all_count_sheet = status_start + '_count_all'
            all_cnt.to_excel(res_writer, sheet_name = all_count_sheet, index = False, header = True)

            kb_month_cnt.to_excel(kb_writer, sheet_name = month_count_sheet, index = False, header = True)
            kb_all_cnt.to_excel(kb_writer, sheet_name = all_count_sheet, index = False, header = True)

        res_writer.save()
        kb_writer.save()

        
        if source_code == 'VT':
            report_out_file = anlys_base_name + source_name + report_end_name
            report_df = wslive_source_df[report_cols]
            report_df.to_csv(report_out_file, index=False, header=True)
            
       
        # If source is MF, compile a list and batch file for known bad entries to use to delete from PPD
        if source_name.find('MF') >= 0 or source_code == 'VT':
            
            # Get all known bad entries, then get index of not in service ones
            known_bad_df = wslive_source_df[wslive_source_df['PHONE_STATUS'] == 'Known Bad']   
            nis_ndx = known_bad_df['COMMENTS'] == 'NOT IN SERVICE'
            
            # find all known bads that are not not in service and merge with the latest PPD to make sure they are
            # still present - if they are not, this means they are already deleted
            not_nis_df = known_bad_df[~nis_ndx]
            not_nis_ppd_df = not_nis_df.merge(ppd_df, how = 'inner', left_on = ['PHYSICIAN_ME_NUMBER', 'OFFICE_TELEPHONE'], 
                                              right_on = ['ME', 'TELEPHONE_NUMBER'])
            not_nis_batch = create_phone_delete(not_nis_ppd_df, 'ME', 'TELEPHONE_NUMBER')
            
            # find all not in service entries and get all PPD entries with the same phone numbers (across all MEs)
            nis_df = known_bad_df[nis_ndx]
            nis_merge_df = nis_df.merge(ppd_df, how = 'inner', left_on = 'OFFICE_TELEPHONE', right_on = 'TELEPHONE_NUMBER')
            nis_uniq_df = nis_merge_df.groupby(['ME', 'TELEPHONE_NUMBER']).first().reset_index()     
            nis_batch = create_phone_delete(nis_uniq_df, 'ME', 'TELEPHONE_NUMBER')
            
            # combine not in service and other known bad dataframes
            kb_uniq_rem_batch = combine_batches(nis_batch, not_nis_batch, 'phone')
            
            num_PPD_kb_entries = nis_uniq_df.shape[0] + not_nis_ppd_df.shape[0]
            
            # report results
            print('\n')
            print('Known Bad Masterfile Results')
            print('----------------------------')
            print('Number of Known Bad WSLive Entries: {}'.format(known_bad_df.shape[0]))
            print('Number of Known Bad Entries Still Present in PPD: {}'.format(num_PPD_kb_entries))
            print('Number of Not In Service WSLive Entries: {}'.format(nis_df.shape[0]))
            print('Number of Other Known Bad WSLive Entries: {}'.format(not_nis_ppd_df.shape[0]))
            print('Number of Not In Service PPD Entries: {}'.format(nis_uniq_df.shape[0]))
            print('Total Number of Phone Numbers To Be Removed: {}'.format(kb_uniq_rem_batch.shape[0]))
                   
            
            kb_del_all_out_file = support_dir + date_range_str + '_' + source_name + '_WSLive_MF_Phones_KnownBad.csv'
            kb_nis_all_out_file = support_dir + date_range_str + '_' + source_name + '_WSLive_MF_Phones_KnownBad_NIS.csv'
            
            # save output analysis files and output batch file
            known_bad_df.to_csv(kb_del_all_out_file, index = False, header = True)       
            nis_uniq_df.to_csv(kb_nis_all_out_file, index = False, header = True)      
            
            if i == 0:
                kb_uniq_comb_batch_df = kb_uniq_rem_batch
            else: 
                kb_uniq_comb_batch_df = combine_batches(kb_uniq_comb_batch_df, kb_uniq_rem_batch, 'phone')
            
        i += 1

    if isinstance(kb_uniq_comb_batch_df, pd.DataFrame):
        kb_del_out_file = batch_out_dir + 'HSG_PHYS_DELETES_' + start_time_str + '_StdKnownBad.csv'
        kb_uniq_comb_batch_df.to_csv(kb_del_out_file, index=False, header=True)
        
        print('\n')
        print('------------------------------------------')
        print('Total unique numbers to be deleted: {}'.format(kb_uniq_comb_batch_df.shape[0]))
        print('------------------------------------------')
            
    # change logging back to console and close log file
    sys.stdout = old_stdout
    log_file.close()

 
def add_zero_counts(type_cnt, status_var):
    
    status_types = ['Confirmed', 'Updated', 'Inconclusive', 'Known Bad', 'No Contact']
    for status in status_types:
        if status not in list(type_cnt[status_var]):
            uniq_yr = list(type_cnt['WS_YEAR'].unique())
            uniq_mon = list(type_cnt['WS_MONTH'].unique())
            
            for year in uniq_yr:
                for month in uniq_mon:
                    if any((type_cnt['WS_YEAR'] == year) & (type_cnt['WS_MONTH'] == month)):
                        temp_row = {'WS_YEAR':year, 'WS_MONTH':month, status_var:status, 'count':0}
                        temp_df = pd.DataFrame(temp_row, index = [0])
                        type_cnt = pd.concat([type_cnt, temp_df], ignore_index=True)
                
            type_cnt = type_cnt.sort_values(['WS_YEAR', 'WS_MONTH'])

    return type_cnt


def get_type_counts(data_df, status_type):
    
    type_month_cnt = data_df.sort_values(['WS_YEAR', 'WS_MONTH', status_type]).groupby(['WS_YEAR', 
                                            'WS_MONTH', status_type]).size().reset_index()
    type_month_cnt = type_month_cnt.rename(columns = {0:'count'})
    type_month_cnt = add_zero_counts(type_month_cnt, status_type)
    
    type_all_cnt = data_df.sort_values([status_type]).groupby([status_type]).size().reset_index()
    type_all_cnt = type_all_cnt.rename(columns = {0:'count'})
    
    kb_df = data_df[data_df[status_type] == 'Known Bad']
    kb_month_cnt = kb_df.sort_values(['WS_YEAR', 'WS_MONTH', 'COMMENTS']).groupby(['WS_YEAR', 
                                            'WS_MONTH', 'COMMENTS']).size().reset_index()
    kb_month_cnt = kb_month_cnt.rename(columns = {0:'count'})

    kb_all_cnt = kb_df.sort_values(['COMMENTS']).groupby(['COMMENTS']).size().reset_index()
    kb_all_cnt = kb_all_cnt.rename(columns = {0:'count'})

    return type_month_cnt, type_all_cnt, kb_month_cnt, kb_all_cnt     
  

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--start-date', required=True,
                    help='WSLive data start date in the form YYYY-MM[-DD] (default day is 1).')
    ap.add_argument('-e', '--end-date', required=True,
                    help='WSLive data end date in the form YYYY-MM[-DD] (default day is last day of month).')
    args = vars(ap.parse_args())

    main(args)
