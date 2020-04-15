# Kari Palmier    9/30/19    Created
#
#############################################################################
import os
import sys

import numpy as np

import datalabs.curate.dataframe  # pylint: disable=unused-import

def replace_nan_str_w_npnan(data_df):   
    
    data_df = data_df.datalabs.upper()
    
    col_names = list(data_df.columns.values)
    for name in col_names:
        data_df[name] = data_df[name].apply(lambda x: np.nan if x == 'NAN' else x)
        
    return data_df
