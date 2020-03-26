import recordlinkage
import pandas

def input_files_create_df():
    aapa = pandas.read_csv('aapa_indexed.csv', index_col='idx')
    state = pandas.read_csv('state_indexed.csv', index_col='idy')

    df_aapa = pandas.DataFrame(aapa)
    df_state = pandas.DataFrame(state)

    return (df_aapa, df_state)

def set_exact_match_rule(df_aapa, df_state):
    indexer = recordlinkage.Index()
    indexer.block('license') #exact match on license
    candidate_links = indexer.index(df_aapa, df_state)
    print(len(candidate_links)) #get possible number of pairs

    return (candidate_links)

def set_matching_rules(candidate_links, df_aapa, df_state):
    compare = recordlinkage.Compare()
    compare.exact('license', 'license', label='license')
    compare.exact('wstate', 'wstate', label='wstate') #workstate
    compare.string('fname', 'fname', method='jarowinkler', label='fname', threshold=0.85)
    compare.string('wal1', 'wal1', method='damerau_levenshtein', label='wal1', threshold=0.7) #workaddress

    # The comparison vectors
    compare_vectors = compare.compute(candidate_links, df_aapa, df_state)

    print(compare_vectors)
    #compare_vectors = compare_vectors[:100] # just to select a subset
    compare_vectors.to_csv('encoded.csv')  # this file stores scores

    return (compare_vectors)


def link_vectors_to_data(compare_vectors, df_aapa, df_state):
    '''Creating a Data frame based on the scores to better understand the match.'''
    print('hi')
    result = pandas.DataFrame()
    for index, row in compare_vectors.iterrows():
        aapa_data_slice = df_aapa.iloc[index[0]].to_frame().T
        state_data_slice = df_state.iloc[index[1]].to_frame().T
        two_rows_compared = pandas.concat([aapa_data_slice, state_data_slice], sort=True)
        result = pandas.concat([result, two_rows_compared], sort=True)

    result.to_csv('result.csv')

def main():
    df_aapa, df_state =  input_files_create_df()
    candidate_links = set_exact_match_rule(df_aapa, df_state)
    compare_vectors = set_matching_rules(candidate_links, df_aapa, df_state)
    link_vectors_to_data(compare_vectors, df_aapa, df_state)


#if __name__ == "__main__":
main()