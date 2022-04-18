# Kari Palmier    8/8/19    Created
# Kari Palmier    8/15/19   Added batch splitting and removed combine wrapper function
#
#############################################################################
import pandas as pd
import datetime

def create_phone_delete(data_df, me_var_name, phone_var_name):
    
    batch_vars = [me_var_name, phone_var_name]
    uniq_batch = data_df[batch_vars]
    uniq_batch['fax'] = ''
    uniq_batch['source'] = ''
    uniq_batch['verified_date'] = ''
    uniq_batch['load_type'] = 'D'
    
    batch_col_map = {me_var_name:'me', phone_var_name:'phone'}
    uniq_batch = uniq_batch.rename(columns = batch_col_map)
    uniq_batch = uniq_batch.groupby(['me', 'phone']).first().reset_index()
    col_order = ['me', 'phone', 'fax', 'source', 'verified_date', 'load_type']
    uniq_batch = uniq_batch[col_order]

    return uniq_batch

def create_phone_append(data_df, me_var_name, phone_var_name, phone_source):
    
    current_time = datetime.datetime.now()
   
    batch_vars = [me_var_name, phone_var_name]
    uniq_batch = data_df[batch_vars]
    uniq_batch['fax'] = ''
    uniq_batch['source'] = phone_source
    uniq_batch['verified_date'] = current_time.strftime("%m/%d/%y")
    uniq_batch['load_type'] = 'A'
     
    batch_col_map = {me_var_name:'me', phone_var_name:'phone'}
    uniq_batch = uniq_batch.rename(columns = batch_col_map)
    uniq_batch = uniq_batch.groupby(['me', 'phone']).first().reset_index()
    col_order = ['me', 'phone', 'fax', 'source', 'verified_date', 'load_type']
    uniq_batch = uniq_batch[col_order]

    return uniq_batch

def create_phone_replace(data_df, me_var_name, phone_var_name, phone_source):
    
    current_time = datetime.datetime.now()
   
    batch_vars = [me_var_name, phone_var_name]
    uniq_batch = data_df[batch_vars]
    uniq_batch['fax'] = ''
    uniq_batch['source'] = phone_source
    uniq_batch['verified_date'] = current_time.strftime("%m/%d/%y")
    uniq_batch['load_type'] = 'R'
     
    batch_col_map = {me_var_name:'me', phone_var_name:'phone'}
    uniq_batch = uniq_batch.rename(columns = batch_col_map)
    uniq_batch = uniq_batch.groupby(['me', 'phone']).first().reset_index()
    col_order = ['me', 'phone', 'fax', 'source', 'verified_date', 'load_type']
    uniq_batch = uniq_batch[col_order]

    return uniq_batch

def create_fax_append(data_df, me_var_name, fax_var_name, phone_source):
    
    current_time = datetime.datetime.now()
   
    batch_vars = [me_var_name, fax_var_name]
    uniq_batch = data_df[batch_vars]
    uniq_batch['phone'] = ''
    uniq_batch['source'] = phone_source
    uniq_batch['verified_date'] = current_time.strftime("%m/%d/%y")
    uniq_batch['load_type'] = 'A'
     
    batch_col_map = {me_var_name:'me', fax_var_name:'fax'}
    uniq_batch = uniq_batch.rename(columns = batch_col_map)
    uniq_batch = uniq_batch.groupby(['me', 'fax']).first().reset_index()
    col_order = ['me', 'phone', 'fax', 'source', 'verified_date', 'load_type']
    uniq_batch = uniq_batch[col_order]

    return uniq_batch

def combine_batches(batch1, batch2, phone_fax_var):
    
    if phone_fax_var != 'fax':
        phone_fax_var = 'phone'
    
    combined_df = pd.concat([batch1, batch2], ignore_index = True)
    uniq_df = combined_df.groupby(['me', phone_fax_var]).first().reset_index()
    
    cols = list(uniq_df.columns.values)
    cols[1] = 'phone'
    cols[2] = 'fax'
    
    uniq_df = uniq_df[cols]
    
    return uniq_df


