# Kari Palmier    Created 7/8/19
#
#############################################################################
import pandas as pd
import sys
import numpy as np

def combine_data(file_paths, index_column, header_row):

    for i in range(len(file_paths)):
            
        file = file_paths[i]
        if file.find('.csv') > 0:
            temp_df = pd.read_csv(file, delimiter = ",", index_col = index_column, header = header_row, dtype = str)
        elif file.find('.xlsx') > 0 or file.find('.xls') > 0:
            temp_df = pd.read_excel(file, index_col = index_column, header = header_row, dtype = str)
        else:
            del_str = str(input(
                    "File type selected is not a csv or Excel file.  Is the file delimited by a different char? (y/n): "))
            if del_str.lower().find('y') >= 0:
                del_type = str(input("Enter the file delimiter (\t for tab for example): "))
                temp_df = pd.read_csv(file, delimiter = del_type, index_col = index_column, 
                                      header = header_row, dtype = str)
            else:
                print("File type is not supported.")
                sys.exit()
            
        if i == 0:
            out_df = temp_df
            orig_col_names = list(temp_df.columns.values)
        else:
            temp_cols = list(temp_df.columns.values)
            all_cols = set(orig_col_names + temp_cols)
            if len(all_cols) != len(orig_col_names):
                out_add_cols = set(temp_cols).difference(orig_col_names)
                temp_add_cols = set(orig_col_names).difference(temp_cols)
                for i in out_add_cols:
                    out_df[i] = np.nan
                for j in temp_add_cols:
                    temp_df[j] = np.nan
                            
            out_df = pd.concat([out_df, temp_df], axis = 0, join = 'outer', ignore_index = True,
                               sort = True)
        
    return out_df            

