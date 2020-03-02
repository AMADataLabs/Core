# Kari Palmier    Created 7/30/19
#
#############################################################################

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import cross_validate
from sklearn import metrics
from sklearn.model_selection import GridSearchCV

import warnings, sklearn.exceptions
warnings.filterwarnings("ignore", category=sklearn.exceptions.ConvergenceWarning)
warnings.filterwarnings("ignore", category=sklearn.exceptions.DataConversionWarning)

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

#############################################################################

# This function randomly under samples the training data and target passed in using imbalanced learn RUS
# Inputs: train_data = training data, train_target = training target, rand_st = random state
#         setting, sample_strat = sampling strategy (distribution of sampled minority and majority
#         classes)
# Outputs: train_data_rus = undersampled training data, train_target_rus = undersampled target

def create_under_data(train_data, train_target, rand_st, sample_strat):

    x_col_names = list(train_data.columns.values)
    y_col_names = list(train_target.columns.values)

    print('Number of Original Target 0 Value: {}'.format(sum(train_target[y_col_names[0]] == 0)))
    print('Number of Original Target 1 Value: {}'.format(sum(train_target[y_col_names[0]] == 1)))
    print('\n')
    
    rus = RandomUnderSampler(random_state = rand_st, sampling_strategy = sample_strat)
    train_data_rus_np, train_target_rus_np = rus.fit_resample(train_data, train_target)

    train_data_rus = pd.DataFrame(train_data_rus_np, columns = x_col_names)
    train_rus_indices = train_data_rus.index.values
    train_target_rus = pd.DataFrame(train_target_rus_np, index = train_rus_indices, 
                                    columns = y_col_names)

    print('Number of Random Under Sample Target 0 Value: {}'.format(sum(train_target_rus[y_col_names[0]] == 0)))
    print('Number of Random Under Sample Target 1 Value: {}'.format(sum(train_target_rus[y_col_names[0]] == 1)))
    
    return train_data_rus, train_target_rus


# This function SMOTE oversamples the training data and target passed in using imbalanced SMOTE
# Inputs: train_data = training data, train_target = training target, rand_st = random state
#         setting, sample_strat = sampling strategy (distribution of sampled minority and majority
#         classes)
# Outputs: train_data_sm = SMOTE oversampled training data, train_target_sm = SMOTE oversampled target

def create_smote_data(train_data, train_target, rand_st, sample_strat):

    x_col_names = list(train_data.columns.values)
    y_col_names = list(train_target.columns.values)

    print('Number of Original Target 0 Value: {}'.format(sum(train_target[y_col_names[0]] == 0)))
    print('Number of Original Target 1 Value: {}'.format(sum(train_target[y_col_names[0]] == 1)))
    print('\n')
    
    sm = SMOTE(random_state=rand_st, sampling_strategy=sample_strat)
    train_data_sm_np, train_target_sm_np = sm.fit_resample(train_data, train_target)

    train_data_sm = pd.DataFrame(train_data_sm_np, columns=x_col_names)
    train_sm_indices = train_data_sm.index.values
    train_target_sm = pd.DataFrame(train_target_sm_np, index=train_sm_indices, columns=y_col_names)

    print('Number of SMOTE Target 0 Value: {}'.format(sum(train_target_sm[y_col_names[0]] == 0)))
    print('Number of SMOTE Target 1 Value: {}'.format(sum(train_target_sm[y_col_names[0]] == 1)))
    
    return train_data_sm, train_target_sm


def create_confusion_mat(pred_vals, test_target, main_scorer, model_scores):
    
    cm = metrics.confusion_matrix(test_target, pred_vals)
    
    main_scorer += '_score'
    score = model_scores[main_scorer]
    
    plt.figure(figsize=(9, 9))
    sns.heatmap(cm, annot=True, fmt="d", linewidths=.5, square=True,
                cmap = 'Blues_r')
    plt.ylabel('Actual label')
    plt.xlabel('Predicted label')
    all_sample_title = 'Predicted Value {} Score: {:0.4f}'.format(main_scorer.upper(), score)
    plt.title(all_sample_title, size=15)
    plt.show()   
    
    return


def get_prob_info(probs):
    
    bin_edges = list(np.arange(0.0, 1.0, 0.1))
    bin_edges.append(1.0)
    plt.hist(probs, bins=bin_edges, alpha=0.5, edgecolor='black', linewidth=1.2)
    plt.xlabel('Prediction Probabilities Of Value 1')
    plt.ylabel('Count')
    plt.title('Histogram of Prediction Probabilities')
    plt.grid(True)
    plt.show()    

def get_class_probabilities(model, data, show_info_flag=False):
    
    probs = model.predict_proba(data)[:, 1]
    
    if show_info_flag:
        get_prob_info(probs)
    
    return probs
    

def get_pred_info(pred_vals):
    
    uniq_vals = np.sort(np.unique(pred_vals))
    counts = [list(pred_vals).count(x) for x in uniq_vals]
    plt.bar(list(uniq_vals.astype('str')), counts, align='center', alpha=0.5)
    plt.ylabel('Count') 
    plt.title('Count of Each Class Predicted')
    plt.show()

    num_0 = sum(pred_vals == 0)
    num_1 = sum(pred_vals == 1)
    perc_0 = num_0/(num_0 + num_1)
    perc_1 = num_1/(num_0 + num_1)
                                    
    print('Number of 0 predictions: {}'.format(num_0))
    print('Number of 1 predictions: {}'.format(num_1))
    print('Percent of predictions with value 0: {}'.format(perc_0))
    print('Percent of predictions with value 1: {}'.format(perc_1))

    
def get_class_predictions(model, data, thresh=0.5, show_info_flag=False):
    
    prob_vals = get_class_probabilities(model, data, show_info_flag)
    
    if thresh == 0.5:
        pred_vals = model.predict(data)
    else:
        pred_vals = np.zeros((len(prob_vals), 1))
        one_ndx = prob_vals >= thresh
        pred_vals[one_ndx] = 1
    
    if show_info_flag:
        get_pred_info(pred_vals)
    
    return pred_vals, prob_vals
    

def create_roc_curve(target, prob):
    
    fpr, tpr, _ = metrics.roc_curve(target, prob)
    roc_auc = metrics.auc(fpr, tpr)
    
    plt.figure()
    lw = 2
    plt.plot(fpr, tpr, color = 'darkorange',
             lw = lw, label = 'ROC curve (area = {:0.2f})'.format(roc_auc))
    plt.plot([0, 1], [0, 1], color = 'navy', lw = lw, linestyle = '--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.show()

    return


def create_pred_scatter(pred_vals, prob_vals):
    
    if len(prob_vals) > 500:
        temp_prob = prob_vals[0:500]
        temp_pred = pred_vals[0:500]
    else:
        temp_prob = prob_vals
        temp_pred = pred_vals
      
    x_vals = range(len(temp_prob))
    
    temp_df = pd.DataFrame(temp_pred, columns = ['class_predictions'])
    temp_df['probabilities'] = temp_prob
    temp_df['data_indices'] = x_vals
    
    # Use the 'hue' argument to provide a factor variable
    sns.lmplot( x = "data_indices", y = "probabilities", data = temp_df, fit_reg = False, 
               hue = 'class_predictions', legend = False)
    plt.title('Prediction Probabilities Colored By Predicted Class')
    plt.legend(loc = 'center left', bbox_to_anchor=(1, 0.5))
    plt.show()



# Expected scorers need to match metrics method naming
# accuracy_score, roc_auc_score, precision_score, recall_score, f1_score
def score_fit_model(pred_vals, test_target, 
                    metric_fcns = ['accuracy_score', 'roc_auc_score']):
    
    model_scores = {}
    metric_fcns.sort()
    for score_type in metric_fcns:        
        if score_type.find('roc') >= 0:
            if isinstance(test_target, pd.DataFrame):
                if len(set(list(test_target.iloc[:, 0]))) == 1:
                    print('ROC invalid for class with only 1 type')
                    continue
            else:
                 if len(set(list(test_target.iloc[:]))) == 1:
                    print('ROC invalid for class with only 1 type')
                    continue
               
        func = getattr(metrics, score_type.lower())
        model_scores[score_type] = func(test_target, pred_vals)
                
    return model_scores


def display_cv_results(scores):
    
    score_keys = [key for key in sorted(scores.keys()) if 'test' in key]
    score_keys.sort()
    
    for key in score_keys:
        print('CV ', key, ': {} +/- {}'.format(scores[key].mean(), 
              scores[key].std() * 2))                                                                                                    

    return


def display_model_results(model_scores):
    
    print('Model Prediction Scores')
    print('-----------------------')
    
    model_keys = list(model_scores.keys())
    model_keys.sort()
    for key in model_keys:
        print(key, ': {}'.format(model_scores[key])) 
                                                                                           
    print('\n')

    return

def display_class_table(train_target, train_pred):
    
    print('Model Prediction Classificaton Table')
    print('------------------------------------')
    
    print(metrics.classification_report(train_target, train_pred))                                                                                         

    return


def evaluate_model(target, preds, probs, metric_fcns, main_scorer):
    
    pred_scores = score_fit_model(preds, target, metric_fcns)
    display_model_results(pred_scores)
    display_class_table(target, preds)
    create_roc_curve(target, preds)
    create_pred_scatter(preds, probs)
    create_confusion_mat(preds, target, main_scorer, pred_scores)

    return pred_scores

# This function performs k-fold cross-validation on training data passed in and reports its
# performance then fits the testing data and reports its performance.
# Inputs: train_data = training data, train_target = training target, test_data = validation data,
#         test_target = validation target, model = sklearn model object, model_type = model type string,
#         model_desc = model description string, cv_num = number of CV folds
# Outputs: fit_model = fitted sklearn model object
def model_data(train_data, train_target, test_data, test_target, model, cv_scorers, 
               cv_num, metric_fcns, main_scorer):
    
    print('*****************************************************************************************')
    print('************************* Training Set Cross-Validation Results *************************')
    print('*****************************************************************************************')
    print('\n')
    start_ts = time.time()
    scores = cross_validate(model, train_data, train_target, scoring = cv_scorers, 
                            cv = cv_num)
    display_cv_results(scores)                                                                                                  
    print("CV Runtime:", time.time() - start_ts)
    print('\n')
    
    # Fit model to entire training dataset
    pred_dict = {}
    scores_dict = {}
    model.fit(train_data, train_target)
    
    print('*****************************************************************************************')
    print('******************************* Full Training Set Results *******************************')
    print('*****************************************************************************************')
    print('\n')
    
    train_pred, train_probs = get_class_predictions(model, train_data)
    pred_dict['train_pred'] = train_pred
    pred_dict['train_probs'] = train_probs
   
    print('\n')
    print('------------------------------------------------------------')
    print('--- All Possible Class Threshold Probabilities ROC Curve ---')
    print('------------------------------------------------------------')
    create_roc_curve(train_target, train_probs)
    
    print('\n')
    print('---------------------------------------')
    print('--- Actual Class Prediction Results ---')
    print('---------------------------------------')
    print('\n')
    train_pred_scores = evaluate_model(train_target, train_pred, train_probs, metric_fcns, main_scorer)
    scores_dict['train_scores'] = train_pred_scores
    
    print('\n')
    
    # Handle the case if the data was not split prior to modeling (original models had this case)
    test_probs = []
    if isinstance(test_data, pd.DataFrame) or isinstance(test_data, np.ndarray):
        print('*****************************************************************************************')
        print('********************************** Testing Set Results **********************************')
        print('*****************************************************************************************')
    
        test_pred, test_probs = get_class_predictions(model, test_data)
        pred_dict['test_pred'] = test_pred
        pred_dict['test_probs'] = test_probs
        
        print('\n')
        print('------------------------------------------------------------')
        print('--- All Possible Class Threshold Probabilities ROC Curve ---')
        print('------------------------------------------------------------')
        create_roc_curve(test_target, test_probs)
        
        print('\n')
        print('---------------------------------------')
        print('--- Actual Class Prediction Results ---')
        print('---------------------------------------')
        print('\n')
        test_pred_scores = evaluate_model(test_target, test_pred, test_probs, metric_fcns, main_scorer)                    
        scores_dict['test_scores'] = test_pred_scores
   
    return model, pred_dict, scores_dict

# This function calls the sklearn GridSearchCV with the model object and parameter list passed in.
# Inputs: model = sklearn model object, train_data = training data, train_target = training target,
#         parameter_dict = dictionary with value lists per model parameter, score = scoring type,
#         cv_num = number of CV folds, model_type = model type string,model_desc = model description
#         string
#         threshold value (used to determine if performance increase is more than noise)
# Outputs: model = sklearn model object containing optimal parameters
def perform_grid_search(model, data_train, target_train, param_dict, score, cv_num):

    print('*** Grid Search ***')
    
    start_ts = time.time()

    gs = GridSearchCV(model, param_dict, verbose = 1, cv = cv_num, scoring = score)
    gs.fit(data_train, target_train)
    opt_params = gs.best_params_
    opt_score = gs.best_score_
    print("Grid Search Runtime:", time.time() - start_ts)
    print('\n')
    print('Grid Search Optimal Parameters:', opt_params)
    print('Grid Search Optimal Parameter Score:', opt_score)
    print('\n')
    
    for key, value in opt_params.items():
        model.set_params(**{key: value})
    print('Optimal Model Parameter Settings:')
    print(model)
    print('\n')
    print('\n')
    print('All Model Results')
    print('-----------------')
    model_results = gs.cv_results_['mean_test_score']

    plt.plot(range(len(model_results)), model_results, color = 'blue', 
             marker = '.', linewidth = 2, markersize = 10)
    plt.ylabel('Model Number') 
    plt.ylabel('CV Result') 
    plt.title('Grid Search Model Results')
    plt.show()

    gs.cv_results_.pop('params', None)    
    gs_result_df = pd.DataFrame(gs.cv_results_)
    
    return model, gs_result_df


def apply_model(model, in_data):
    
    preds, probs = get_class_predictions(model, in_data)

    return preds, probs
    
    
    
