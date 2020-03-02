# Kari Palmier    9/30/19    Created
#
#############################################################################

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'Common_Code\\'
sys.path.insert(0, gen_path)

def remove_col_name_float_pt(data_df):   
    
    col_names = list(data_df.columns.values)
    new_col_dict = {}
    for name in col_names:
        pt_ndx = name.find('.0')
        if pt_ndx > 0:
            new_col_dict[name] = name[:pt_ndx]
        else:
            new_col_dict[name] = name
            
    data_df = data_df.rename(columns = new_col_dict)   
    
    return data_df
