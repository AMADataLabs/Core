# Kari Palmier    9/9/19    Created
#
#############################################################################
import pandas as pd


def get_mult_var_null_df(comp_df, var_names, null_compare_type):
    
    for i in range(len(var_names)):

        if null_compare_type == 'notnull':
            res_ndx = comp_df[var_names[i]].notnull()
        else:
            res_ndx = comp_df[var_names[i]].isna()

        if i == 0:
            total_ndx = res_ndx
        else:
            total_ndx = total_ndx & res_ndx
            
    filtered_df = comp_df.loc[total_ndx, :]
    
    return filtered_df, total_ndx

def get_var_completeness(comp_df, ppd_df, comp_var_name, ppd_var_name, ppd_join_var, comp_join_var, comp_name):
    
    complete_res_dict = {}

    complete_res_dict['comp_total_cnt'] = comp_df.shape[0]

    if isinstance(comp_var_name, list):
        comp_not_null, total_ndx = get_mult_var_null_df(comp_df, comp_var_name, 'notnull')
    else:
        comp_not_null = comp_df[comp_df[comp_var_name].notnull()]
    complete_res_dict['comp_var_not_null_cnt'] = comp_not_null.shape[0]
    
    complete_res_dict['ppd_total_cnt'] = ppd_df.shape[0]
    
    if isinstance(ppd_var_name, list):
        ppd_not_null, total_ndx = get_mult_var_null_df(ppd_df, ppd_var_name, 'notnull')
    else:
        ppd_not_null = ppd_df[ppd_df[ppd_var_name].notnull()]
    complete_res_dict['ppd_var_not_null_cnt'] = ppd_not_null.shape[0]

    comp_ppd_match_df = comp_df.merge(ppd_df, how = 'inner', 
                                     right_on = ppd_join_var , left_on = comp_join_var)
    complete_res_dict['entry_match_cnt'] = comp_ppd_match_df.shape[0]
    
    if isinstance(comp_var_name, list):
        temp_ppd_df, no_ppd_ndx = get_mult_var_null_df(comp_ppd_match_df, ppd_var_name, 'isna')
        temp_comp_df, no_comp_ndx = get_mult_var_null_df(comp_ppd_match_df, comp_var_name, 'isna')
    else:
        no_ppd_ndx = comp_ppd_match_df[ppd_var_name].isna()
        no_comp_ndx = comp_ppd_match_df[comp_var_name].isna()

    match_no_ppd_phone_df = comp_ppd_match_df.loc[no_ppd_ndx, :]
    complete_res_dict['entry_match_ppd_var_null_cnt'] = match_no_ppd_phone_df.shape[0]

    match_ppd_phone_df = comp_ppd_match_df.loc[~no_ppd_ndx, :]
    complete_res_dict['entry_match_ppd_var_not_null_cnt'] = match_ppd_phone_df.shape[0]

    match_no_comp_phone_df = comp_ppd_match_df.loc[no_comp_ndx, :]
    complete_res_dict['entry_match_comp_var_null_cnt'] = match_no_comp_phone_df.shape[0]

    match_comp_phone_df = comp_ppd_match_df.loc[~no_comp_ndx, :]
    complete_res_dict['entry_match_comp_var_not_null_cnt'] = match_comp_phone_df.shape[0]

    match_no_nan_df = comp_ppd_match_df.loc[~no_ppd_ndx & ~no_comp_ndx, :]
    complete_res_dict['entry_match_no_var_null_cnt'] = match_no_nan_df.shape[0]

    if isinstance(comp_var_name, list):
        for i in range(len(comp_var_name)):
    
            res_ndx = match_no_nan_df[comp_var_name[i]] == match_no_nan_df[ppd_var_name[i]]
    
            if i == 0:
                same_ndx = res_ndx
            else:
                same_ndx = total_ndx & res_ndx
    else:          
        same_ndx = match_no_nan_df[comp_var_name] == match_no_nan_df[ppd_var_name]
        
    same_phone_df = match_no_nan_df.loc[same_ndx, :]
    complete_res_dict['entry_match_var_same_cnt'] = same_phone_df.shape[0]

    not_same_phone_df = match_no_nan_df.loc[~same_ndx, :]
    complete_res_dict['entry_match_var_diff_cnt'] = not_same_phone_df.shape[0]
    
    complete_res_df = pd.DataFrame(complete_res_dict, index = [0])
    complete_res_df = complete_res_df.T
    complete_res_df = complete_res_df.rename(columns = {0:'count'})

     
    if isinstance(ppd_var_name, list):
        save_var = 'TOTAL_ADDRESS'
    else:
        save_var = ppd_var_name

    print('PPD/{} {} Comparison'.format(comp_name, save_var.upper()))
    print('---------------------------------------------------------------')
    
    print('Total number {} entries: {}'.format(comp_name, complete_res_df.loc['comp_total_cnt', 'count']))
    print('Number {} entries with {} present: {}'.format(comp_name,save_var, 
          complete_res_df.loc['comp_var_not_null_cnt', 'count']))
    print('\n')
    print('Total number PPD entries: {}'.format(complete_res_df.loc['ppd_total_cnt', 'count']))
    print('Number PPD entries with {} present: {}'.format(save_var, 
          complete_res_df.loc['ppd_var_not_null_cnt', 'count']))
    print('\n')
    print('Number matching ME entries between PPD and {}: {}'.format(comp_name, 
          complete_res_df.loc['entry_match_cnt', 'count']))
    print('\n')
    print('Number matching ME entries missing PPD {}: {}'.format(save_var, 
          complete_res_df.loc['entry_match_ppd_var_null_cnt', 'count']))
    print('Number matching ME entries present PPD {}: {}'.format(save_var, 
          complete_res_df.loc['entry_match_ppd_var_not_null_cnt', 'count']))
    print('\n')
    print('Number matching ME entries missing {} {}: {}'.format(comp_name, save_var, 
          complete_res_df.loc['entry_match_comp_var_null_cnt', 'count']))
    print('Number matching ME entries present {} {}: {}'.format(comp_name, save_var, 
          complete_res_df.loc['entry_match_comp_var_not_null_cnt', 'count']))
    print('\n')
    print('Number of matching ME entries with {} and PPD {}: {}'.format(comp_name, save_var, 
          complete_res_df.loc['entry_match_no_var_null_cnt', 'count']))
    print('\n')
    print('Number of matching ME entries with same {}: {}'.format(save_var, 
          complete_res_df.loc['entry_match_var_same_cnt', 'count']))
    print('Number of matching ME entries with different {}: {}'.format(save_var, 
          complete_res_df.loc['entry_match_var_diff_cnt', 'count']))
    print('\n')



    return complete_res_df

def get_ppd_comp_comparison(comp_df, ppd_df, ppd_join_var, comp_join_var, comp_name):
    
    ppd_comp_dict = {}

    ppd_comp_dict['comp_total_cnt'] = comp_df.shape[0]
    
    ppd_comp_dict['ppd_total_cnt'] = ppd_df.shape[0]
    
    comp_ppd_null_df = comp_df.merge(ppd_df, how = 'left', 
                                     right_on = ppd_join_var , left_on = comp_join_var)
    comp_only_df = comp_ppd_null_df[comp_ppd_null_df[ppd_join_var].isna()]
    ppd_comp_dict['entry_not_in_ppd_cnt'] = comp_only_df.shape[0]
    
    comp_null_ppd_df = comp_df.merge(ppd_df, how = 'right', 
                                     right_on = ppd_join_var , left_on = comp_join_var)
    ppd_only_df = comp_null_ppd_df[comp_null_ppd_df[comp_join_var].isna()]
    ppd_comp_dict['entry_not_in_comp_cnt'] = ppd_only_df.shape[0]
    
    comp_ppd_match_df = comp_df.merge(ppd_df, how = 'inner', 
                                     right_on = ppd_join_var , left_on = comp_join_var)
    ppd_comp_dict['entry_match_cnt'] = comp_ppd_match_df.shape[0]
    
    ppd_comp_df = pd.DataFrame(ppd_comp_dict, index = [0])
    ppd_comp_df = ppd_comp_df.T
    ppd_comp_df = ppd_comp_df.rename(columns = {0:'count'})
     
    print('Total number {} entries: {}'.format(comp_name, ppd_comp_df.loc['comp_total_cnt', 'count']))
    print('Total number PPD entries: {}'.format(ppd_comp_df.loc['ppd_total_cnt', 'count']))
    print('Number of PPD DPC entries: {}'.format(ppd_comp_df.shape[0]))
    print('\n')
    print('Number {} ME entries missing from PPD: {}'.format(comp_name, ppd_comp_df.loc['entry_not_in_ppd_cnt', 'count']))
    print('Number PPD ME entries missing from {}: {}'.format(comp_name, ppd_comp_df.loc['entry_not_in_comp_cnt', 'count']))
    print('\n')
    print('Number PPD and {} matching ME entries: {}'.format(comp_name, ppd_comp_df.loc['entry_match_cnt', 'count']))
    print('\n')

    return ppd_comp_df
    
    
    

    
