import recordlinkage
import pandas

aapa = pandas.read_csv('aapa_indexed.csv',index_col='idx' )
state = pandas.read_csv('state_indexed.csv',index_col='idy' )

df_a = pandas.DataFrame(aapa)
df_b = pandas.DataFrame(state)

indexer = recordlinkage.Index()
indexer.block('license')
candidate_links = indexer.index(df_a, df_b)

#get possible number of pairs
print(len(candidate_links))

#set business rules
compare = recordlinkage.Compare()
compare.exact('license', 'license', label='license')
compare.exact('wstate', 'wstate', label='wstate')
compare.string('fname', 'fname', method='jarowinkler', label='fname', threshold=0.85)
compare.string('wal1', 'wal1', method='damerau_levenshtein', label='wal1', threshold=0.7)


# The comparison vectors
compare_vectors = compare.compute(candidate_links, df_a, df_b)

print(compare_vectors)


#compare_vectors = compare_vectors[:3000] # just to select a subset
compare_vectors.to_csv('encoded.csv') #this file stores scores

'''Creating a Data frame based on the scores to better understand the match.'''
result = pandas.DataFrame()
for index, row in compare_vectors.iterrows():
    s = df_a.iloc[index[0]].to_frame().T
    ss = df_b.iloc[index[1]].to_frame().T
    resulty = pandas.concat([s, ss], sort=True)
    result = pandas.concat([result, resulty], sort=True)

result.to_csv('result.csv')