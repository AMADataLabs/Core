# Kari Palmier   9/20/19    Created
#
#############################################################################

def rename_post_cols(data_df):
    col_names = data_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('post') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'post_' + name
            new_col_dict[name] = new_name
            
    data_df = data_df.rename(columns = new_col_dict)
    
    return data_df


def rename_comm_cols(data_df):
    col_names = data_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('ent_comm') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'ent_comm_' + name
            new_col_dict[name] = new_name
            
    data_df = data_df.rename(columns = new_col_dict)
    
    return data_df


def rename_usg_cols(data_df):
    col_names = data_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('usg') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'usg_' + name
            new_col_dict[name] = new_name
            
    data_df = data_df.rename(columns = new_col_dict)
    
    return data_df


def rename_email_cols(data_df):
    col_names = data_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('email') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'email_' + name
            new_col_dict[name] = new_name
            
    data_df = data_df.rename(columns = new_col_dict)
    
    return data_df


def rename_phn_cols(data_df):
    col_names = data_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('phn') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'phn_' + name
            new_col_dict[name] = new_name
            
    data_df = data_df.rename(columns = new_col_dict)
    
    return data_df


def rename_fone_zr_cols(data_df):
    col_names = data_df.columns.values
    new_col_dict = {}
    for name in col_names:
        if name.find('FNZR') >= 0:
            new_col_dict[name] = name
        else:
            new_name = 'FNZR_' + name
            new_col_dict[name] = new_name
            
    data_df = data_df.rename(columns = new_col_dict)
    
    return data_df
