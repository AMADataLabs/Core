# Kari Palmier    8/20/19    Created
#
#############################################################################

def capitalize_df_contents(data_df):   
    col_names = list(data_df.columns.values)
    for name in col_names:
        data_df[name] = data_df[name].apply(lambda x: x.upper() if isinstance(x, str) else x)
        
    return data_df
