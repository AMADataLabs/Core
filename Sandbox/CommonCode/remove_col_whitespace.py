# Kari Palmier    Created 8/22/19
#
#############################################################################

def remove_col_whitespace(data_df):
    
    col_names = list(data_df.columns.values)
    for name in col_names:
        name_ndx = col_names.index(name)
        if sum(data_df[name].notnull()) > 0:
            if isinstance(data_df[data_df[name].notnull()].iloc[0, name_ndx], str):
                data_df[name] = data_df[name].apply(lambda x: x.strip() if x != None else x)
           
    return data_df

