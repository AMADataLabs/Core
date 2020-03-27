# Kari Palmier    7/31/19    Created 
# Kari Palmier    8/14/19    Update to make get_sample more generic for other data usage
#
#########################################################################################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Get path of general (common) code and add it to the python path variable
import sys
import os
curr_path = os.path.abspath(__file__)
slash_ndx = [i for i in range(len(curr_path)) if curr_path.startswith('\\', i)]
base_path = curr_path[:slash_ndx[-2]+1]
gen_path = base_path + 'CommonCode\\'
sys.path.insert(0, gen_path)

from filter_bad_phones import get_good_bad_phones
import datalabs.curate.dataframe as df

import warnings
warnings.filterwarnings("ignore")


def get_prob_info(probs):
    
    bin_edges = list(np.arange(0.0, 1.0, 0.1))
    bin_edges.append(1.0)
    plt.hist(probs, bins = bin_edges, alpha = 0.5, edgecolor = 'black', linewidth = 1.2)
    plt.xlabel('Prediction Probabilities Of Value 1')
    plt.ylabel('Count')
    plt.title('Prediction Probabilities - Class Threshold is 0.5')
    plt.grid(True)
    plt.show()    


def get_bin_info():
    
    sample_bin_lls = []
    sample_bin_uls = []
    samples_per_bin = []
    exit_loop = False
    while not exit_loop:
        
        sample_bin_lls.append(float(input('Enter the current bin lower limit (included in bin): ')))
        sample_bin_uls.append(float(input('Enter the current bin upper limit (not included in bin): ')))
        
        temp_sz = input('Enter the current bin sample size (all = all samples in bin): ')
        if temp_sz.lower() == 'all':
            samples_per_bin.append('all')
        else:
            samples_per_bin.append(int(temp_sz))
                
        exit_str = input('Do you want to enter another bin ([y]/n)?: ')
        exit_str = exit_str.upper()
        
        if exit_str.find('N') >= 0:
            exit_loop = True
            
    print('\n')
    return sample_bin_lls, sample_bin_uls, samples_per_bin 


def get_uniq_entries(data_df, me_var_name, sample_var_name, prob_var_name, model_type = 1, print_flag = False):
    
    if print_flag:
        print('\n')
        
        if model_type == 2:
            print('Number of records before removing duplicate {}: {}'.format(sample_var_name, 
                  data_df.shape[0]))
        else:
            print('Number of records before removing duplicate {}/{}: {}'.format(me_var_name, 
                  sample_var_name, data_df.shape[0]))
            
    orig_col_order = data_df.columns.values
    
    if model_type == 2:
        uniq_df = data_df.sort_values([sample_var_name, prob_var_name], 
                                                     ascending  = True).groupby(sample_var_name).first().reset_index()
    else:
        uniq_df = data_df.groupby([me_var_name, sample_var_name]).apply(lambda x: x.sample(1)).reset_index(drop = True)
        
    uniq_df = uniq_df[orig_col_order]
        
    if print_flag:
        print('\n')
        
        if model_type == 2:
            print('Number of records after removing duplicate {}: {}'.format(sample_var_name, 
                  uniq_df.shape[0]))
        else:
            print('Number of records after removing duplicate {}/{}: {}'.format(me_var_name, 
                  sample_var_name, uniq_df.shape[0]))
        
    return uniq_df
   

def filter_repeated_phones(data_df, sample_var_name, dup_threshold):
    
    uniq_phone_df = data_df.sort_values([sample_var_name]).groupby([sample_var_name]).size().reset_index()
    uniq_phone_df = uniq_phone_df.rename(columns = {0:'count'})
    
    dup_df = uniq_phone_df[uniq_phone_df['count'] > dup_threshold]
    dup_phones = list(dup_df[sample_var_name])
    
    filtered_df = data_df[~data_df[sample_var_name].isin(dup_phones)]
    
    i = 0
    for i in range(len(dup_phones)):
        
        curr_phone = dup_phones[i]   
        curr_phone_df = data_df[data_df[sample_var_name] == curr_phone]
        
        curr_rand_df = curr_phone_df.sample(dup_threshold)    
        filtered_df = pd.concat([filtered_df, curr_rand_df], axis = 0, ignore_index = True)
        
    print('Number of records after replacing duplicate numbers with subsample: {}'.format(filtered_df.shape[0]))

    return filtered_df
        

def get_phone_sample(model_pred_df, sample_bin_lls, sample_bin_uls, samples_per_bin, prob_var_name,
               sample_var_name, model_type, *argv):
     
    if len(argv) > 0:          
        me_var_name = argv[0]
        dup_threshold = argv[1]
        print_flag = argv[2]
    else:
        me_var_name = ''
        dup_threshold = 0
        print_flag = False
        
    """ PURE RANDOM SAMPLE """
    if prob_var_name not in model_pred_df.columns.values:
        model_pred_df[prob_var_name] = 1.0


    bad_df, model_pred_df = get_good_bad_phones(model_pred_df, sample_var_name)

    model_pred_df[prob_var_name] = model_pred_df[prob_var_name].astype('float')
    
    uniq_pred_df = get_uniq_entries(model_pred_df, me_var_name, sample_var_name, prob_var_name, model_type, print_flag)

    if sample_bin_lls == [] or sample_bin_uls == [] or samples_per_bin == []:
        get_prob_info(uniq_pred_df[prob_var_name])
        sample_bin_lls, sample_bin_uls, samples_per_bin = get_bin_info()
        
    sample_buff_mult = 3
    for i in range(len(sample_bin_lls)):
        
        current_ll = sample_bin_lls[i]
        current_ul = sample_bin_uls[i]
        current_bin_sz = samples_per_bin[i]
        
        if float(current_ul) == 1.0:
            temp_df = uniq_pred_df[(uniq_pred_df[prob_var_name] >= current_ll) & \
                                      (uniq_pred_df[prob_var_name] <= current_ul)]
        else:
            temp_df = uniq_pred_df[(uniq_pred_df[prob_var_name] >= current_ll) & \
                                      (uniq_pred_df[prob_var_name] < current_ul)]
        
        if str(current_bin_sz).lower() == 'all':
            rand_df = temp_df
        else:
            buffer_sample_sz = current_bin_sz * sample_buff_mult
            if (current_bin_sz * sample_buff_mult) > temp_df.shape[0]:
                buffer_df = temp_df
            else:
                buffer_df = temp_df.sample(buffer_sample_sz)
            
        if model_type == 1:
            filtered_df = filter_repeated_phones(buffer_df, sample_var_name, dup_threshold)
        else:
            filtered_df = model_pred_df
            
        rand_df = filtered_df.sample(current_bin_sz)
    
        if print_flag:
            print('Number of points between {} and {} total: {}'.format(current_ll, current_ul, temp_df.shape[0]))
            print('Number of points between {} and {} in sample: {}'.format(current_ll, current_ul, rand_df.shape[0]))
            print('\n')
        
        if i == 0:
            sample_df = rand_df[:]
        else:
            sample_df = pd.concat([sample_df, rand_df])    
            
        current_ll = sample_bin_uls[i]
                 
    return sample_df, filtered_df
    
             
def format_phone_sample_cols(sample_df, sample_vars):
    
    sample_df = df.rename_in_upper_case(sample_df)
    cap_sample_vars = []

    for var in sample_vars:
        cap_sample_vars.append(var.upper())
    
    new_col_names = []
    col_dict = {}
    for name in cap_sample_vars:
    
        ndx = name.find('PPD_')
        if name.find('PPD_ME_PAD') >= 0:
            new_name = 'ME'
        elif name.find('PPD_PE_CD_PAD') >= 0:
            new_name = 'PE_CD'
        elif ndx >= 0:
            start_ndx = ndx + len('PPD_')
            new_name = name[start_ndx:]            
        elif name.find('PE_DESCRIPTION') >= 0:
            new_name = 'DESCRIPTION'       
        else:
            new_name = name
    
        new_col_names.append(new_name)
        col_dict[name] = new_name
       
    new_sample_df = sample_df.rename(columns=col_dict)

    pred_cols = ['PRED_CLASS', 'PRED_PROBABILITY']
    for c in pred_cols:
        if c not in new_sample_df.columns.values:
            new_col_names.remove(c)

    new_sample_df = new_sample_df[new_col_names]
    
    new_sample_df = new_sample_df.replace('NAN', '')          
        
    if 'ME' in new_col_names:
        if str(new_sample_df['ME'].dtypes) == 'int' or str(new_sample_df['ME'].dtypes) == 'int64':
            new_sample_df['ME'] =  new_sample_df['ME'].apply(lambda x: '{0:0>11}'.format(x))
            
        if str(new_sample_df['ME'].dtypes) == 'float'or str(new_sample_df['ME'].dtypes) == 'float64':
            new_sample_df['ME'] =  new_sample_df['ME'].astype('str').apply(lambda x: x[:-2]).astype('int64')
            new_sample_df['ME'] =  new_sample_df['ME'].apply(lambda x: '{0:0>11}'.format(x))

    return new_sample_df, new_col_names