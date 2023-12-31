""" Review for deletion """
# pylint: disable=no-name-in-module,import-error,wildcard-import,undefined-variable,protected-access,unused-import,too-many-instance-attributes,logging-fstring-interpolation,unnecessary-lambda,abstract-class-instantiated,logging-format-interpolation,no-member,trailing-newlines,trailing-whitespace,function-redefined,use-a-generator,f-string-without-interpolation,invalid-name,bare-except,unnecessary-comprehension,unused-variable
import logging
import numpy as np
import pandas as pd
from sklearn import metrics

from class_model_creation import score_fit_model

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pylint: disable=too-many-statements
def class_results(wslive_pred_df):
    num_0 = sum(wslive_pred_df['ACTUAL_CLASS'] == 0)
    num_1 = sum(wslive_pred_df['ACTUAL_CLASS'] == 1)
    perc_0 = num_0/(num_0 + num_1)
    perc_1 = num_1/(num_0 + num_1)

    LOGGER.info('Actual (Phone Survey) Result Information')
    LOGGER.info('----------------------------------------')
    LOGGER.info('Number of total results: %s\n', wslive_pred_df.shape[0])

    LOGGER.info('1 Label = Phone survey result was Confirmed')
    LOGGER.info('0 Label = Phone survey results was Not Confirmed\n')

    LOGGER.info('Number of 0 actual results: %s', num_0)
    LOGGER.info('Number of 1 actual results: %s', num_1)
    LOGGER.info('Percent of actual results with value 0: %s', perc_0)
    LOGGER.info('Percent of actual results with value 1: %s\n', perc_1)

    conf_mat = metrics.confusion_matrix(wslive_pred_df['ACTUAL_CLASS'], wslive_pred_df['PRED_CLASS'])
    LOGGER.info('Actual/Predicted Confusion Matrix')
    LOGGER.info('--------------------------------------')
    LOGGER.info(conf_mat)
    LOGGER.info('\n')

    class_mat = metrics.classification_report(
        wslive_pred_df['ACTUAL_CLASS'], wslive_pred_df['PRED_CLASS'], output_dict=True
    )
    class_mat_df = pd.DataFrame(class_mat['0'], index=['0'])
    class_mat_df = pd.concat([class_mat_df, pd.DataFrame(class_mat['1'], index=['1'])], axis=0)
    class_mat_df = pd.concat([class_mat_df, pd.DataFrame(class_mat['macro avg'], index=['macro avg'])], axis=0)
    class_mat_df = pd.concat([class_mat_df, pd.DataFrame(class_mat['weighted avg'], index=['weighted avg'])], axis=0)

    num_rows = class_mat_df.shape[0] + 1
    num_cols = class_mat_df.shape[1] + 1
    pd.set_option('max_rows', num_rows)
    pd.set_option('max_columns', num_cols)

    LOGGER.info('Actual/Predicted Classification Report')
    LOGGER.info('--------------------------------------')
    LOGGER.info(class_mat_df)
    LOGGER.info('\n')

    metric_fcns = ['accuracy_score', 'roc_auc_score', 'precision_score', 'recall_score', 'f1_score']
    actual_scores = score_fit_model(wslive_pred_df['PRED_CLASS'], wslive_pred_df['ACTUAL_CLASS'], metric_fcns)

    actual_scores['TN_count'] = conf_mat[0][0]
    actual_scores['FP_count'] = conf_mat[0][1]
    actual_scores['FN_count'] = conf_mat[1][0]
    actual_scores['TP_count'] = conf_mat[1][1]

    score_df = pd.DataFrame(actual_scores, index=[0])
    score_df = score_df.T
    score_df = score_df.rename(columns={0:'score'})

    num_rows = score_df.shape[0] + 1
    num_cols = score_df.shape[1] + 1
    pd.set_option('max_rows', num_rows)
    pd.set_option('max_columns', num_cols)

    LOGGER.info('Actual/Predicted Classification Scores')
    LOGGER.info('--------------------------------------')
    LOGGER.info(score_df)
    LOGGER.info('\n')

    return conf_mat, class_mat_df, score_df


def binned_results(wslive_pred_df, bin_step, status_var):
    bin_lower_bounds = list(np.arange(0, 1, bin_step))
    bin_upper_bounds = list(np.arange(bin_step, (1 + bin_step), bin_step))
    bins = []

    for bin_bounds in zip(bin_lower_bounds, bin_upper_bounds):
        bins.append(_bin_data(wslive_pred_df, status_var, bin_bounds))

    return pd.concat(bins, axis=0, ignore_index=True)


# pylint: disable=too-many-statements
def _bin_data(wslive_pred_df, status_var, bin_bounds):
    status_types = ['CONFIRMED', 'UPDATED', 'INCONCLUSIVE', 'KNOWN BAD', 'NO CONTACT']

    if float(bin_bounds[1]) == 1.0:
        temp_df = wslive_pred_df[(wslive_pred_df['PRED_PROBABILITY'] >= bin_bounds[0]) & \
                                  (wslive_pred_df['PRED_PROBABILITY'] <= bin_bounds[1])]
    else:
        temp_df = wslive_pred_df[(wslive_pred_df['PRED_PROBABILITY'] >= bin_bounds[0]) & \
                                  (wslive_pred_df['PRED_PROBABILITY'] < bin_bounds[1])]


    temp_phone_cnt = temp_df.sort_values([status_var]).groupby([status_var]).size().reset_index()
    temp_phone_cnt = temp_phone_cnt.rename(columns={0:'count'})

    temp_bin_dict = {'bin_ul':round(bin_bounds[1], 2)}
    total_count = 0
    for status in status_types:
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

    return pd.DataFrame(temp_bin_dict)
