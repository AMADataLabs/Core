from class_model_creation import get_prob_info, get_pred_info

def scoring_statistics(scored_data):
    get_prob_info(scored_data['PRED_PROBABILITY'])
    get_pred_info(scored_data['PRED_CLASS'])
