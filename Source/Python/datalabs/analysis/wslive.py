""" Functions for analysis of scored WSLive survey results. """
import os
import sys

import numpy as np
import pandas as pd
from sklearn import metrics

from class_model_creation import score_fit_model


def class_results(wslive_pred_df):
    
    num_0 = sum(wslive_pred_df['ACTUAL_CLASS'] == 0)
    num_1 = sum(wslive_pred_df['ACTUAL_CLASS'] == 1)
    perc_0 = num_0/(num_0 + num_1)
    perc_1 = num_1/(num_0 + num_1)
                          
    print('Actual (Phone Survey) Result Information')
    print('----------------------------------------')
    print('Number of total results: {}'.format(wslive_pred_df.shape[0]))
    print('\n')
    print('1 Label = Phone survey result was Confirmed')
    print('0 Label = Phone survey results was Not Confirmed')
    print('\n')
    
    print('Number of 0 actual results: {}'.format(num_0))
    print('Number of 1 actual results: {}'.format(num_1))
    print('Percent of actual results with value 0: {}'.format(perc_0))
    print('Percent of actual results with value 1: {}'.format(perc_1))
    print('\n')
    
    conf_mat = metrics.confusion_matrix(wslive_pred_df['ACTUAL_CLASS'], wslive_pred_df['PRED_CLASS'])
    print('Actual/Predicted Confusion Matrix')
    print('--------------------------------------')
    print(conf_mat)
    print('\n')
    
    class_mat = metrics.classification_report(wslive_pred_df['ACTUAL_CLASS'], wslive_pred_df['PRED_CLASS'], output_dict=True)
    class_mat_df = pd.DataFrame(class_mat['0'], index = ['0'])
    class_mat_df = pd.concat([class_mat_df, pd.DataFrame(class_mat['1'], index = ['1'])], axis = 0)
    class_mat_df = pd.concat([class_mat_df, pd.DataFrame(class_mat['macro avg'], index = ['macro avg'])], axis = 0)
    class_mat_df = pd.concat([class_mat_df, pd.DataFrame(class_mat['weighted avg'], index = ['weighted avg'])], axis = 0)
    
    num_rows = class_mat_df.shape[0] + 1
    num_cols = class_mat_df.shape[1] + 1
    pd.set_option('max_rows', num_rows)
    pd.set_option('max_columns', num_cols)
    
    print('Actual/Predicted Classification Report')
    print('--------------------------------------')
    print(class_mat_df)
    print('\n')
    
    metric_fcns = ['accuracy_score', 'roc_auc_score', 'precision_score', 'recall_score', 'f1_score']
    actual_scores = score_fit_model(wslive_pred_df['PRED_CLASS'], wslive_pred_df['ACTUAL_CLASS'], metric_fcns)
    
    actual_scores['TN_count'] = conf_mat[0][0]
    actual_scores['FP_count'] = conf_mat[0][1]
    actual_scores['FN_count'] = conf_mat[1][0]
    actual_scores['TP_count'] = conf_mat[1][1]
    
    score_df = pd.DataFrame(actual_scores, index = [0])
    score_df = score_df.T
    score_df = score_df.rename(columns = {0:'score'})
    
    num_rows = score_df.shape[0] + 1
    num_cols = score_df.shape[1] + 1
    pd.set_option('max_rows', num_rows)
    pd.set_option('max_columns', num_cols)
        
    print('Actual/Predicted Classification Scores')
    print('--------------------------------------')
    print(score_df)
    print('\n')
    
    return conf_mat, class_mat_df, score_df


def binned_results(wslive_pred_df, bin_step, status_var):
    
    sample_bin_lls = list(np.arange(0, 1, bin_step))
    sample_bin_uls = list(np.arange(bin_step, (1 + bin_step), bin_step))
    
    status_types = ['CONFIRMED', 'UPDATED', 'INCONCLUSIVE', 'KNOWN BAD', 'NO CONTACT']
    for i in range(len(sample_bin_lls)):
        
        current_ll = sample_bin_lls[i]
        current_ul = sample_bin_uls[i]
        
        if float(current_ul) == 1.0:
            temp_df = wslive_pred_df[(wslive_pred_df['PRED_PROBABILITY'] >= current_ll) & \
                                      (wslive_pred_df['PRED_PROBABILITY'] <= current_ul)]
        else:
            temp_df = wslive_pred_df[(wslive_pred_df['PRED_PROBABILITY'] >= current_ll) & \
                                      (wslive_pred_df['PRED_PROBABILITY'] < current_ul)]
         
        
        temp_phone_cnt = temp_df.sort_values([status_var]).groupby([status_var]).size().reset_index()
        temp_phone_cnt = temp_phone_cnt.rename(columns = {0:'count'})
        
        temp_bin_dict = {'bin_ul':round(current_ul, 2)}
        total_count = 0
        for j in range(len(status_types)):
            
            status = status_types[j]
            
            status_ndx = temp_phone_cnt[status_var] == status
            
            if any(status_ndx):
                temp_bin_dict[status] = int(temp_phone_cnt.loc[status_ndx, 'count'])
            else:
                temp_bin_dict[status] = 0
                
            total_count += temp_bin_dict[status]    
              
        if total_count > 0:
            temp_bin_dict['total_count'] = total_count
            temp_bin_dict['acc_total'] = temp_bin_dict['CONFIRMED'] / total_count
            temp_bin_dict['acc_wo_no_cont'] = temp_bin_dict['CONFIRMED'] / (total_count - \
                         temp_bin_dict['NO CONTACT'])
            temp_bin_dict['acc_wo_inc_no_cont'] = temp_bin_dict['CONFIRMED'] / (total_count - \
                         (temp_bin_dict['INCONCLUSIVE'] + temp_bin_dict['NO CONTACT']))
            temp_bin_dict['prop_kb'] = temp_bin_dict['KNOWN BAD'] / total_count
        else:
            temp_bin_dict['total_count'] = 0
            temp_bin_dict['acc_total'] = 0
            temp_bin_dict['acc_wo_no_cont'] = 0
            temp_bin_dict['acc_wo_inc_no_cont'] = 0
            temp_bin_dict['prop_kb'] = 0
                        
        if i == 0:
            bin_df = pd.DataFrame(temp_bin_dict, index = [0])
        else:
            num_rows = bin_df.shape
            temp_bin_df = pd.DataFrame(temp_bin_dict, index = [num_rows])
            bin_df = pd.concat([bin_df, temp_bin_df], axis = 0, ignore_index = True)
        
    return bin_df
    
    
    
    
    
