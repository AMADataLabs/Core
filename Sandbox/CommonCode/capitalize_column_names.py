# Kari Palmier    8/20/19    Created
#
#############################################################################

def capitalize_column_names(data_df):   
    col_names = list(data_df.columns.values)
    new_col = {}
    for name in col_names:
        new_col[name] = name.upper()
    
    data_df = data_df.rename(columns=new_col)
    
    return data_df
