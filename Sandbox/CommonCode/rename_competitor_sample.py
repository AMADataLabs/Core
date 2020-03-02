# Kari Palmier    8/22/19    Created
#
#############################################################################

def rename_competitor_sample(data_df, comp_prefix):
    
    data_cols = list(data_df.columns.values)
    col_dict = {}
    for name in data_cols:
        ims_ndx = name.find(comp_prefix)
        if ims_ndx >= 0:
            base_name = name[(ims_ndx + len(comp_prefix)):]
            
            if base_name in data_cols:
                data_df = data_df.drop([base_name], axis = 1)              
                col_dict[name] = base_name

    renamed_df = data_df.rename(columns = col_dict)
    
    return renamed_df
