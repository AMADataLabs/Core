import pandas as pd
from nameparser import HumanName
# import settings
# import os

def get_data():
    all_cpt_data = pd.read_excel("C:/Users/vigrose/Data/CPT_Panel/Panel_Evals.xlsx")
    cpt_data = pd.read_excel("C:/Users/vigrose/Data/CPT_Panel/Panel_Evals.xlsx", header = 1)
    cpt_col = all_cpt_data.columns
    return(all_cpt_data, cpt_data, cpt_col)

def pivot(cpt_data, cpt_col):
    names = [x for x in cpt_col if "Unnamed" not in x]
    cols = [0,1,2,3,4,5,6,7]
    dict_list = []
    for name in names:
        data = cpt_data.iloc[:, cols]
        for row in data.itertuples():
            row_list = list(row)
            reviewer = HumanName(row.Name).last
            question_number = 2
            for question_column in cols[1:]:
                new_dict = {
                'Peer': name,
                'Reviewer': reviewer,
                'Question': f'Q{question_number}',
                'Rating': row_list[question_number]
            }
                question_number+=1
                dict_list.append(new_dict)
        cols = [(x + 7) if x != 0 else x for x in cols]
    return dict_list

def clean(raw_data):
    dicto ={}
    index = 0
    for col in raw_data.columns:
        index += 1
        if "Unnamed" in col:
            new_col = f'Column{index}'
            dicto[col] = new_col
    raw_data = raw_data.rename(columns=dicto)
    return raw_data

def main():
    all_cpt_data, cpt_data, cpt_col = get_data()
    dict_list = pivot(cpt_data, cpt_col)
    overall = pd.DataFrame(dict_list)
    numerical = overall[overall.Question!='Q8'].dropna(subset=['Rating'])
    numerical.to_excel('C:/Users/vigrose/Data/CPT_Panel/bah.xlsx', index=False)
    numerical['Rating'] = numerical.Rating.astype(float)
    peer_average = numerical.groupby('Peer').mean()
    peer_question_average = numerical.groupby(['Peer', 'Question']).mean()
    comments = overall[overall.Question=='Q8'].dropna(subset=['Rating']).drop(columns='Question')
    median = numerical.groupby(['Peer', 'Question']).median()
    qpr_rating = numerical.groupby(['Question']).mean()
    peer_rev_rating = numerical.groupby(['Peer', 'Reviewer']).mean()
    rev_q_rating = numerical.groupby(['Reviewer', 'Question']).mean()
    review_avg_rating = numerical.groupby(['Reviewer']).mean()
    all_cpt_data = clean(all_cpt_data)
    with pd.ExcelWriter('C:/Users/vigrose/Data/CPT_Panel/transformed_2020-10-01.xlsx') as writer:  
        all_cpt_data.to_excel(writer, sheet_name='Raw', index=False)
        overall.to_excel(writer, sheet_name='Overall', index=False)
        numerical.to_excel(writer, sheet_name='Rating(2)', index=False)
        numerical.to_excel(writer, sheet_name='Rating', index=False)
        numerical.to_excel(writer, sheet_name='Original_Rating', index=False)
        comments.to_excel(writer, sheet_name='Comments', index=False)
        peer_question_average.to_excel(writer, sheet_name='QPRRating')
        median.to_excel(writer, sheet_name='Median')
        peer_rev_rating.to_excel(writer, sheet_name='PeerRevRating')
        rev_q_rating.to_excel(writer, sheet_name='RevQRating')
        review_avg_rating.to_excel(writer, sheet_name='ReviewerAvgRating')
        peer_average.to_excel(writer, sheet_name='PeerAvgRating')
        qpr_rating.to_excel(writer, sheet_name='QPRRating_Average')

if __name__ == "__main__":
    main()