# Kari Palmier    9/30/19    Created
#
#############################################################################
import numpy as np

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

from capitalize_df_contents import capitalize_df_contents

def replace_nan_str_w_npnan(data_df):   
    
    data_df = capitalize_df_contents(data_df)
    
    col_names = list(data_df.columns.values)
    for name in col_names:
        data_df[name] = data_df[name].apply(lambda x: np.nan if x == 'NAN' else x)
        
    return data_df
