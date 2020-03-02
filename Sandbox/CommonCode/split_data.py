# Kari Palmier    9/19/19    Created
#
#############################################################################

def split_data(data_df, split_sizes):
    
    data_df_list = []
    data_index_list = []
    for i in range(len(split_sizes)):
    
        if i == 0:
            curr_split = data_df[:]
            
        if split_sizes[i] > curr_split.shape[0]:
            print('Sample size {} is too large for remaining dataframe size ({})'.format(split_sizes[i], 
                  curr_split.shape[0]))
            return -1
        
        curr_sample = curr_split.sample(split_sizes[i]) 
        data_df_list.append(curr_sample)
        data_index_list.append(curr_sample.index)
        
        curr_split = curr_split[~curr_split.index.isin(curr_sample.index)]  
        
    
    data_df_list.append(curr_split)    
        
    return data_df_list, data_index_list
