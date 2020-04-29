""" Function to rank a set of physician data scored for POLO fitness. """

def rank(scored_data):
    scored_data['RANK_ROUND'] = scored_data['PRED_PROBABILITY'].apply(lambda x: round((x * 10)))
    zero_ndx = scored_data['RANK_ROUND'] == 0
    scored_data.loc[zero_ndx, 'RANK_ROUND'] = 1

    return scored_data
