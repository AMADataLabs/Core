import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from nameparser import HumanName
import me_match as match


file_location = input("Enter roster file location:  ")

df = pd.read_csv(file_location)
ppd = pd.read_csv('ppd_spec.csv')

df = match.split_names(df)
df = df.drop_duplicates('NAME')

specs = list(df['SPECIALTY'].unique())
bad_spec = ['Physician Assistant',
 'Nurse Practitioner',
 'Anesthesia - CRNA',
 'Midwife',
 'Anesthesia - CRNA, Nurse Practitioner',
 'Chiropractor',
 'Psychologist',
 'Optometrist',
 'Pediatric Dentistry',
 'Veterinarian',
 'Midwife, Nurse Practitioner']
specs = [x for x in specs if x not in bad_spec]

df = df[df['SPECIALTY'].isin(specs)]

duplicate_names, missing_names, matched= match.match_ppd_name(ppd, df)

new_matched = match.match_ppd_spec_fuzzy(duplicate_names)
new_duplicates, new_matches = match.count_matches(new_matched)
matched = matched.append(new_matches)

new_matched_2 = match.match_ppd_state(new_duplicates)
new_duplicates_2, new_matches_2 = match.count_matches(new_matched_2)
matched = matched.append(new_matches_2)

new_matched_3 = match.match_ppd_city(new_duplicates_2)
new_duplicates_3, new_matches_3 = match.count_matches(new_matched_3)
matched = matched.append(new_matches_3)

new_matched_4 = match.match_ppd_middle(new_duplicates_3)
new_duplicates_4, new_matches_4 = match.count_matches(new_matched_4)
matched = matched.append(new_matches_4)

new_matched_5 = match.match_ppd_spec_hard(new_duplicates_4)
new_duplicates_5, new_matches_5 = match.count_matches(new_matched_5)
matched = matched.append(new_matches_5)

missing_df = df[df.NAME.isin(missing_names)]

missing_matches = pd.DataFrame((match.find_missing_1(missing_df,ppd) + match.find_missing_2(missing_df,ppd)))

missing_matches = pd.merge(df, missing_matches, on = 'NAME')
missing_matches = pd.merge(ppd, missing_matches, on = 'ME')
missing_matches = missing_matches.drop_duplicates(['NAME','ME'])

pd.DataFrame(match.clean_missing_matches(missing_matches)).transpose()