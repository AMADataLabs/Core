# Kari Palmier    Created 7/30/19
#
#############################################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.feature_selection import RFE, VarianceThreshold, SelectFromModel
from sklearn.feature_selection import SelectPercentile, SelectKBest
from sklearn.feature_selection import mutual_info_classif, chi2, f_classif
from sklearn.model_selection import cross_validate

import warnings, sklearn.exceptions
warnings.filterwarnings("ignore", category=sklearn.exceptions.ConvergenceWarning)
warnings.filterwarnings("ignore", category=sklearn.exceptions.DataConversionWarning)
warnings.filterwarnings("ignore")


#############################################################################

def get_model_type(model):
    
    model_str = str(model.get_params)
    ndx1 = model_str.find('get_params of ') + len('get_params of ')
    ndx2 = model_str.find('(')
    model_type_str = model_str[ndx1:ndx2].strip()
    
    return model_type_str

# This function creates lists of feature names to keep and to delete based on the
# sel_idx passed in (if sel_idx is 1, the feature should be kept
# Inputs: col_names = list of data set features names, sel_idx = list containing
#        value of 1 if the column feature should be kept and 0 if deleted
# Outputs: keep_cols = list of feature names to keep, del_cols = list of feature
#         names to delete
def get_keep_del_cols(col_names, sel_idx):
    keep_cols = []
    del_cols = []
    for i in range(len(col_names)):
        if sel_idx[i] == 1:                                                           
            keep_cols.append(col_names[i])
        else:                                       
            del_cols.append(col_names[i])

    return keep_cols, del_cols

# This function finds the optimal value of a set of results
# The optimal value is defined as the lowest number of features with the highest AUC
# Instead of finding a general maximum as the optimal value, the optimal values is
# required to be the auc_thresh value higher than the previous value
# This will eliminate the possibility that the optimal value is chosen as the highest
# number of features even though there were less number of features with similar AUC
# Inputs: auc_results = list of CV AUC results from feature selection, auc_thresh = CV 
#        AUC threshold value (used to determine if performance increase is more than noise)
# Outputs: opt_ndx = index value of optimal feature selection result found based on
#          auc threshold
def find_optimal_index(auc_results, score_thresh):
    opt_ndx = 0
    curr_res = 0
    for i in range(len(auc_results)):
        if i == 0 or (auc_results[i] - curr_res) > score_thresh:
            opt_ndx = i
            curr_res = auc_results[i]

    return opt_ndx

# loop_test_type is either "percent", "k", "thresh", "rfe"
def create_score_df(model, score_func, loop_vals, data_np, target_np, cv_scorers, cv_num,
                    loop_test_type, *args):
    
    if len(args) == 1:
        rfe_step = args[0]
    
    feature_select = []    
    results_np0 = np.zeros((len(loop_vals), len(cv_scorers)))
    results_np1 = np.zeros((len(loop_vals), len(cv_scorers)))
    mean_results = pd.DataFrame(results_np0, index = range(len(loop_vals)))
    std_results = pd.DataFrame(results_np1, index = range(len(loop_vals)))
    
    for i in range(len(loop_vals)):  

        val = loop_vals[i]
        if loop_test_type.lower() == "percent":                                                                                                           
            sel = SelectPercentile(score_func, percentile = val)
        elif loop_test_type.lower() == "k":
            sel = SelectKBest(score_func, k = val)
        elif loop_test_type.lower() == "thresh":
            sel = VarianceThreshold(threshold = val)
        elif loop_test_type.lower() == "rfe":
            sel = RFE(model, n_features_to_select = val,step = rfe_step)
        else:
            return;
        
        data_np_fs = sel.fit_transform(data_np, target_np)
        
        try:
            scores = cross_validate(model, data_np_fs, target_np, scoring = cv_scorers, 
                                    cv = cv_num)
        except:
            mean_results = 0
            std_results = 0
            feature_select = 0
                
        else:    
            
            if val == loop_vals[0]:
                score_keys = [key for key in sorted(scores.keys()) if 'test' in key]
                            
                mean_results.columns = score_keys
                std_results.columns = score_keys
            
            for key in score_keys:
                mean_results.loc[i, key] = scores[key].mean()
                std_results.loc[i, key] = scores[key].std() * 2
                
            feature_select.append(sel.get_support())

    return mean_results, std_results, feature_select
    

def display_results(mean_results, std_results, perc_vals, optimal_ndx, col_names, keep_cols,
                    x_desc):
    
    score_names = list(mean_results.columns.values)
    
    if x_desc != '':
        print('{} Selected: {}'.format(x_desc, perc_vals[optimal_ndx]))
    
    for score in score_names:
        print('Selected Model CV Mean ', score, ' Score: {}'.format(
                mean_results.loc[optimal_ndx, score]))
        print('Selected Model CV ', score, ' Deviation: {}'.format(
                std_results.loc[optimal_ndx, score]))
        
    print('Number of Original Features: {}'.format(len(col_names)))
    print('Number of Selected Features: {}'.format(len(keep_cols)))
    
    print('Selected Features:')
    print(keep_cols)
    
    return

def plot_results(main_mean_results, loop_vals, optimal_ndx, main_scorer, score_func_desc,
                 x_desc):
    
    optimal_val = loop_vals[optimal_ndx]
    plt_title = score_func_desc + ' Feature Selection CV ' +  main_scorer + \
        ' Versus ' + x_desc
    plt_ylabel = 'CV ' + main_scorer
    plot_xlabel = x_desc + ' Selected'
    plt.figure()
    plt.xlabel(plot_xlabel)
    plt.ylabel(plt_ylabel)
    plt.title(plt_title)   
    plt.plot(loop_vals, main_mean_results)
    plt.plot(optimal_val, main_mean_results[optimal_ndx], 'x', c='k')
    plt.show()   

    return


def select_best_fs_type(score_df, main_scorer, score_thresh, var_buffer_perc, num_total):
    
    print('Scores Per Feature Selection Type:')
    print(score_df)
    print('\n')
    
    score_cols = list(score_df.columns.values)
    type_ndx = score_cols.index('fs_type')
    score_ndx = score_cols.index('opt_score')
    var_ndx = score_cols.index('num_vars')
    
    var_buffer = int(var_buffer_perc * num_total)

    num_scores = score_df.shape[0]
    for i in range(num_scores):
        if i == 0:
            opt_type = score_df.iloc[i, type_ndx]
            opt_score = score_df.iloc[i, score_ndx]
            opt_num_vars = score_df.iloc[i, var_ndx]
        else:
            tmp_type = score_df.iloc[i, type_ndx]
            tmp_score = score_df.iloc[i, score_ndx]
            tmp_num_vars = score_df.iloc[i, var_ndx]
                        
            if (tmp_score > opt_score or (opt_score - tmp_score) < score_thresh):
                if tmp_num_vars >= (num_total * 0.01):
                    if ((tmp_score - opt_score) > score_thresh or 
                        tmp_num_vars < (opt_num_vars + var_buffer)):
                        opt_type = tmp_type
                        opt_score = tmp_score
                        opt_num_vars = tmp_num_vars
            
    print('Optimal Feature Selection Choice Based On ', main_scorer, ':')
    print('FS Type: ', opt_type)
    print('FS Score: ', opt_score)
    print('\n')
    
    plt.bar(score_df['fs_type'], score_df['opt_score'], align = 'center', alpha = 0.5)
    plt.ylabel('CV Scores') 
    plt.xlabel('Features Selection Types')
    plt.title('Feature Selection CV Scores')
    plt.show()
    
    return opt_score, opt_type


# This function performs chi-squared univariate feature selection.  Feature selection is
# performed for each percentage value given in the perc_vals input list.  The optimal
# percentage is obtained using the find_optimal_index function.  Once the optimal percentage
# is found, corresponding lists of features to delete and keep are generated using
# get_keep_del_cols.  The list of features to delete is then used to generate training
# data that only contains the features to be kept by removing the features to delete.
# Inputs: data_df = training data, target_df = target data, model = sklearn model object,
#         perc_vals = list of percentage values to use for model selection, cv_num =
#         number of CV folds, auc_thresh = CV AUC threshold value (used to determine if
#         performance increase is more than noise)
# Outputs: new_data_df = training data with only features to keep present, del_cols =
#          list of features delete from data
# All scorers:
#    scorers = {'accuracy': 'accuracy', 'roc_auc': 'roc_auc', 'prec': 'precision', 
#               'recall': 'recall', 'bal_accuracy': 'balanced_accuracy'}   
def univariate_chisq_select(data_df, target_df, model, perc_vals = list(range(10, 100, 10)), 
                            cv_num = 5, scorers = {'roc_auc': 'roc_auc'}, 
                            main_scorer = 'roc_auc', score_thresh = 0.01):
    
    col_names = list(data_df.columns.values)
    data_np = data_df.values
    target_np = target_df.values

    print('-- Univariate Chi-Sq Feature Selection --')

    mean_results, std_results, feature_select = create_score_df(model, chi2, 
                                                                perc_vals, data_np, 
                                                                target_np, scorers, 
                                                                cv_num, 'percent')
    if isinstance(mean_results, pd.DataFrame):
        
        main_scorer = 'test_' + main_scorer
        main_mean_results = list(mean_results[main_scorer])
    
        optimal_ndx = find_optimal_index(main_mean_results, score_thresh)
        sel_idx = feature_select[int(optimal_ndx)]
    
        keep_cols, del_cols = get_keep_del_cols(col_names, sel_idx)
                
        display_results(mean_results, std_results, perc_vals, optimal_ndx, col_names, keep_cols,
                        'Percent of Features')
    
        new_data_df = data_df.drop(del_cols, axis = 1)
        
        plot_results(main_mean_results, perc_vals, optimal_ndx, main_scorer, 'Chi-Squared',
                     'Percent of Features')
            
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = main_mean_results[optimal_ndx]
        temp_dict['num_vars'] = len(keep_cols)
        score_df = pd.DataFrame(temp_dict, index = [0])
    
    else:
    
        new_data_df = []
        del_cols = []
        
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = 0
        temp_dict['num_vars'] = 0
        score_df = pd.DataFrame(temp_dict, index = [0])
        
    return new_data_df, del_cols, score_df

# This function performs mutual information feature selection.  Feature selection is
# performed for each percentage value given in the perc_vals input list.  The optimal
# percentage is obtained using the find_optimal_index function.  Once the optimal percentage
# is found, corresponding lists of features to delete and keep are generated using
# get_keep_del_cols.  The list of features to delete is then used to generate training
# data that only contains the features to be kept by removing the features to delete.
# Inputs: data_df = training data, target_df = target data, model = sklearn model object,
#         perc_vals = list of percentage values to use for model selection, cv_num =
#         number of CV folds, auc_thresh = CV AUC threshold value (used to determine if
#         performance increase is more than noise)
# Outputs: new_data_df = training data with only features to keep present, del_cols =
#          list of features delete from data
def mutual_info_select(data_df, target_df, model, perc_vals = list(range(10, 110, 10)), 
                            cv_num = 5, scorers = {'roc_auc': 'roc_auc'}, 
                            main_scorer = 'roc_auc', score_thresh = 0.01):
    
    col_names = list(data_df.columns.values)
    data_np = data_df.values
    target_np = target_df.values

    print('-- Mutual Information Feature Selection --')

    mean_results, std_results, feature_select = create_score_df(model, mutual_info_classif, 
                                                                perc_vals, data_np, 
                                                                target_np, scorers, 
                                                                cv_num, 'percent')

    if isinstance(mean_results, pd.DataFrame):
        
        main_scorer = 'test_' + main_scorer
        main_mean_results = list(mean_results[main_scorer])
    
        optimal_ndx = find_optimal_index(main_mean_results, score_thresh)
        sel_idx = feature_select[int(optimal_ndx)]
    
        keep_cols, del_cols = get_keep_del_cols(col_names, sel_idx)
                
        display_results(mean_results, std_results, perc_vals, optimal_ndx, col_names, keep_cols,
                        'Percent of Features')
    
        new_data_df = data_df.drop(del_cols, axis = 1)
        
        plot_results(main_mean_results, perc_vals, optimal_ndx, main_scorer, 'Mutual Info',
                     'Percent of Features')
        
        temp_dict = {}
        temp_dict['fs_type'] = 'mutinf'
        temp_dict['opt_score'] = main_mean_results[optimal_ndx]
        temp_dict['num_vars'] = len(keep_cols)
        score_df = pd.DataFrame(temp_dict, index = [0])
        
    else:
    
        new_data_df = []
        del_cols = []
        
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = 0
        temp_dict['num_vars'] = 0
        score_df = pd.DataFrame(temp_dict, index = [0])

    return new_data_df, del_cols, score_df

# This function performs anova f statistic feature selection.  Feature selection is
# performed for each percentage value given in the perc_vals input list.  The optimal
# percentage is obtained using the find_optimal_index function.  Once the optimal percentage
# is found, corresponding lists of features to delete and keep are generated using
# get_keep_del_cols.  The list of features to delete is then used to generate training
# data that only contains the features to be kept by removing the features to delete.
# Inputs: data_df = training data, target_df = target data, model = sklearn model object,
#         perc_vals = list of percentage values to use for model selection, cv_num =
#         number of CV folds, auc_thresh = CV AUC threshold value (used to determine if
#         performance increase is more than noise)
# Outputs: new_data_df = training data with only features to keep present, del_cols =
#          list of features delete from data
def anova_f_select(data_df, target_df, model, perc_vals = list(range(10, 110, 10)), 
                            cv_num = 5, scorers = {'roc_auc': 'roc_auc'}, 
                            main_scorer = 'roc_auc', score_thresh = 0.01):
    
    col_names = list(data_df.columns.values)
    data_np = data_df.values
    target_np = target_df.values

    print('-- Anova F Statistic Feature Selection --')

    mean_results, std_results, feature_select = create_score_df(model, f_classif, 
                                                                perc_vals, data_np, 
                                                                target_np, scorers, 
                                                                cv_num, 'percent')

    if isinstance(mean_results, pd.DataFrame):
        
        main_scorer = 'test_' + main_scorer
        main_mean_results = list(mean_results[main_scorer])
    
        optimal_ndx = find_optimal_index(main_mean_results, score_thresh)
        sel_idx = feature_select[int(optimal_ndx)]
    
        keep_cols, del_cols = get_keep_del_cols(col_names, sel_idx)
                
        display_results(mean_results, std_results, perc_vals, optimal_ndx, col_names, keep_cols,
                        'Percent of Features')
    
        new_data_df = data_df.drop(del_cols, axis = 1)
        
        plot_results(main_mean_results, perc_vals, optimal_ndx, main_scorer, 'Anova F Statistic',
                     'Percent of Features')
        
        temp_dict = {}
        temp_dict['fs_type'] = 'anovaf'
        temp_dict['opt_score'] = main_mean_results[optimal_ndx]
        temp_dict['num_vars'] = len(keep_cols)
        score_df = pd.DataFrame(temp_dict, index = [0])

    else:
    
        new_data_df = []
        del_cols = []
        
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = 0
        temp_dict['num_vars'] = 0
        score_df = pd.DataFrame(temp_dict, index = [0])


    return new_data_df, del_cols, score_df


def model_wrapper_select(data_df, target_df, model, thresh_type = 'mean', 
                         max_feats = None, cv_num = 5, scorers = {'roc_auc': 'roc_auc'}, 
                         main_scorer = 'roc_auc'):

    col_names = list(data_df.columns.values)
    data_np = data_df.values
    target_np = target_df.values

    print('-- Model Wrapper Feature Selection --')

    sel = SelectFromModel(model, prefit = False, threshold = thresh_type, 
                          max_features = max_feats) 

    data_np_fs = sel.fit_transform(data_np, target_np)
    
    try:
        scores = cross_validate(model, data_np_fs, target_np, scoring = scorers, 
                                cv = cv_num)

    except:
        new_data_df = []
        del_cols = []
        
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = 0
        temp_dict['num_vars'] = 0
        score_df = pd.DataFrame(temp_dict, index = [0])
            
    else:    
   
        results_np0 = np.zeros((1, len(scorers)))
        results_np1 = np.zeros((1, len(scorers)))
        mean_results = pd.DataFrame(results_np0, index = [0])
        std_results = pd.DataFrame(results_np1, index = [0])
        
        score_keys = [key for key in sorted(scores.keys()) if 'test' in key]
        
        mean_results.columns = score_keys
        std_results.columns = score_keys
        
        for key in score_keys:
            mean_results.loc[0, key] = scores[key].mean()
            std_results.loc[0, key] = scores[key].std() * 2
    
       
        sel_idx = sel.get_support()
        keep_cols, del_cols = get_keep_del_cols(col_names, sel_idx)
                
        display_results(mean_results, std_results, [0], 0, col_names, keep_cols, '')
    
        new_data_df = data_df.drop(del_cols, axis = 1)
        
        main_scorer = 'test_' + main_scorer
        main_mean_results = list(mean_results[main_scorer])
    
        temp_dict = {}
        temp_dict['fs_type'] = 'wrap'
        temp_dict['opt_score'] = main_mean_results[0]
        temp_dict['num_vars'] = len(keep_cols)
        score_df = pd.DataFrame(temp_dict, index = [0])

    return new_data_df, del_cols, score_df
                

def stepwise_recur_select(data_df, target_df, model, k_vals = list(range(1, 20, 1)), 
                          cv_num = 5, scorers = {'roc_auc': 'roc_auc'}, 
                          main_scorer = 'roc_auc', score_thresh = 0.01, step_val = 0.1):

    col_names = list(data_df.columns.values)
    data_np = data_df.values
    target_np = target_df.values

    print('-- RFE Stepwise Feature Selection --')

    mean_results, std_results, feature_select = create_score_df(model, None, 
                                                                k_vals, data_np, 
                                                                target_np, scorers, 
                                                                cv_num, 'rfe', step_val)

    if isinstance(mean_results, pd.DataFrame):
        
        main_scorer = 'test_' + main_scorer
        main_mean_results = list(mean_results[main_scorer])
    
        optimal_ndx = find_optimal_index(main_mean_results, score_thresh)
        sel_idx = feature_select[int(optimal_ndx)]
    
        keep_cols, del_cols = get_keep_del_cols(col_names, sel_idx)
                
        display_results(mean_results, std_results, k_vals, optimal_ndx, col_names, keep_cols,
                        'Number of Features')
    
        new_data_df = data_df.drop(del_cols, axis = 1)
        
        plot_results(main_mean_results, k_vals, optimal_ndx, main_scorer, 'RFE Stepwise',
                     'Number of Features')
        
        temp_dict = {}
        temp_dict['fs_type'] = 'step'
        temp_dict['opt_score'] = main_mean_results[optimal_ndx]
        temp_dict['num_vars'] = len(keep_cols)
        score_df = pd.DataFrame(temp_dict, index = [0])

    else:
    
        new_data_df = []
        del_cols = []
        
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = 0
        temp_dict['num_vars'] = 0
        score_df = pd.DataFrame(temp_dict, index = [0])

    return new_data_df, del_cols, score_df


def low_var_filter(data_df, target_df, model, thresh_vals = list(np.arange(0,1,0.1)), 
                   cv_num = 5, scorers = {'roc_auc': 'roc_auc'}, 
                   main_scorer = 'roc_auc', score_thresh = 0.01):

    col_names = list(data_df.columns.values)
    data_np = data_df.values
    target_np = target_df.values
    
    print('-- Low Variance Filter Feature Selection --')

    mean_results, std_results, feature_select = create_score_df(model, None, 
                                                                thresh_vals, data_np, 
                                                                target_np, scorers, 
                                                                cv_num, 'thresh')

    if isinstance(mean_results, pd.DataFrame):
        
        main_scorer = 'test_' + main_scorer
        main_mean_results = list(mean_results[main_scorer])
    
        optimal_ndx = find_optimal_index(main_mean_results, score_thresh)
        sel_idx = feature_select[int(optimal_ndx)]
    
        keep_cols, del_cols = get_keep_del_cols(col_names, sel_idx)
                
        display_results(mean_results, std_results, thresh_vals, optimal_ndx, col_names, keep_cols,
                        'Thresholds')
    
        new_data_df = data_df.drop(del_cols, axis = 1)
        
        plot_results(main_mean_results, thresh_vals, optimal_ndx, main_scorer, 
                     'Low Variance Filter', 'Thresholds')
    
        temp_dict = {}
        temp_dict['fs_type'] = 'lvf'
        temp_dict['opt_score'] = main_mean_results[optimal_ndx]
        temp_dict['num_vars'] = len(keep_cols)
        score_df = pd.DataFrame(temp_dict, index = [0])

    else:
    
        new_data_df = []
        del_cols = []
        
        temp_dict = {}
        temp_dict['fs_type'] = 'chisq'
        temp_dict['opt_score'] = 0
        temp_dict['num_vars'] = 0
        score_df = pd.DataFrame(temp_dict, index = [0])

    return new_data_df, del_cols, score_df


# This function calls the feature selection functions then saves their outputs into a 
# dictionary.
# Inputs: train_data = training data, train_target = training target, test_data = 
#         test data, test_target = validation target, model = sklearn model object, 
#         perc_vals = list of percentage values to use in feature selection, 
#         k_vals = list of number of features used in RFE stepwise recursive,
#         thresh_vals = list of thresholds for low variance filter, 
#         cv_num = number of CV folds, scorers = types of scores to calculate,
#         main_scorer = scorer to use to select number of features,
#         threshold value (used to determine if performance increase is more than noise),
#         step_val = step value for RFE stepwise recursive
# Outputs: results_dict = dictionary containing training data, list of deleted columns, and model
#          objects for each feature selection type
def perform_feat_sel_models(train_data, train_target, test_data, 
                            model, perc_vals, k_vals, thresh_vals, 
                            cv_num, scorers, main_scorer, score_thresh, var_buffer_perc,
                            step_val):
    
    model_type = get_model_type(model)
    
    results_dict = {}
    
    ##### Perform low variance filter feature selection #####
    train_data_lvf, del_cols_lvf, lvf_score_df = low_var_filter(train_data, train_target, 
                                                  model, thresh_vals, cv_num, 
                                                  scorers, main_scorer, score_thresh) 
    all_scores_df = lvf_score_df
        
    print('\n')
    test_data_lvf = test_data.drop(del_cols_lvf, axis = 1)
    
    results_dict['lvf'] = {'train_data':train_data_lvf, 'test_data':test_data_lvf,
                'del_cols':del_cols_lvf}

    if (model_type.find('MLPClassifier') < 0 and model_type.find('SVC') < 0):
        
        ##### Perform model wrapper feature selection #####
        train_data_wrap, del_cols_wrap, wrap_score_df = model_wrapper_select(train_data, 
                                                            train_target, model, 
                                                            'mean', None, cv_num,
                                                            scorers, main_scorer) 
        all_scores_df = pd.concat([all_scores_df, wrap_score_df])
        
        print('\n')
        test_data_wrap = test_data.drop(del_cols_wrap, axis = 1)

        results_dict['wrap'] = {'train_data':train_data_wrap, 'test_data':test_data_wrap,
                    'del_cols':del_cols_wrap}
        

        ##### Perform RFE stepwise recursive feature selection #####
        train_data_step, del_cols_step, step_score_df = stepwise_recur_select(train_data, 
                                                             train_target, model,  
                                                             k_vals, cv_num,
                                                             scorers, main_scorer,
                                                             score_thresh, step_val)
        all_scores_df = pd.concat([all_scores_df, step_score_df])
       
        print('\n')
        test_data_step = test_data.drop(del_cols_step, axis = 1)

        results_dict['step'] = {'train_data':train_data_step, 'test_data':test_data_step,
                    'del_cols':del_cols_step}
   
    ##### Perform univariate chi-squared feature selection #####
    train_data_chisq, del_cols_chisq, chisq_score_df = univariate_chisq_select(train_data, train_target, 
                                                             model, perc_vals, cv_num,
                                                             scorers, main_scorer,
                                                             score_thresh)
    all_scores_df = pd.concat([all_scores_df, chisq_score_df])

    print('\n')
    test_data_chisq = test_data.drop(del_cols_chisq, axis = 1)
    
    results_dict['chisq'] = {'train_data':train_data_chisq, 'test_data':test_data_chisq,
                'del_cols':del_cols_chisq}

    ##### Perform mutual information feature selection #####
    train_data_mutinf, del_cols_mutinf, mutinf_score_df = mutual_info_select(train_data, train_target, 
                                                            model, perc_vals, cv_num,
                                                            scorers, main_scorer,
                                                            score_thresh)
    all_scores_df = pd.concat([all_scores_df, mutinf_score_df])

   
    print('\n')
    test_data_mutinf = test_data.drop(del_cols_mutinf, axis = 1)
        
    results_dict['mutinf'] = {'train_data':train_data_mutinf, 'test_data':test_data_mutinf,
                'del_cols':del_cols_mutinf}
 
    ##### Perform ANOVA f statistic feature selection #####
    train_data_anovaf, del_cols_anovaf, anovaf_score_df = anova_f_select(train_data, train_target, 
                                                            model, perc_vals, cv_num,
                                                            scorers, main_scorer,
                                                            score_thresh)
    all_scores_df = pd.concat([all_scores_df, anovaf_score_df])
   
    print('\n')
    test_data_anovaf = test_data.drop(del_cols_anovaf, axis = 1)
        
    results_dict['anovaf'] = {'train_data':train_data_anovaf, 'test_data':test_data_anovaf,
                'del_cols':del_cols_anovaf}
    
    # Get best feature selection type based on scoring
    opt_fs_score, opt_fs_type = select_best_fs_type(all_scores_df, main_scorer, score_thresh,
                                                    var_buffer_perc, train_data.shape[1])
    opt_fs_dict = results_dict[opt_fs_type]
    
    return results_dict, opt_fs_dict, all_scores_df
#    return results_dict, all_scores_df

