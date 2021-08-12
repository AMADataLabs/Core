'''
Make scorecard
'''
import os
from datetime import datetime, date
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


def newest(path, text):
    '''Grabs newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

def get_email_data(email_file):
    '''Get email data'''
    em_tbl = pd.read_excel(email_file, header=2)
    email_count = int(em_tbl.iloc[2, 1])
    email_correctness = em_tbl.iloc[3, 1]
    return(email_count, email_correctness)

def get_do_counts(do_file):
    '''Get do counts'''
    with open(do_file, 'r') as file_:
        read_file = file_.read()
        phys_count = int(read_file.split('\n')[0].replace('Physicians: ', '').replace(',', ''))
        stu_count = int(read_file.split('\n')[1].replace('Students: ', '').replace(',', ''))
    return phys_count, stu_count

def read_ppd(ppd_file_location):
    '''Read ppd'''
    ppd = pd.read_csv(ppd_file_location, low_memory=False)

    #Nones
    ppd['ADDRESS_UNDELIVERABLE_FLAG_2'] = ppd['ADDRESS_UNDELIVERABLE_FLAG'].fillna('None')
    ppd['PRESUMED_DEAD_FLAG_2'] = ppd['PRESUMED_DEAD_FLAG'].fillna('None')

    #Everybody gotta be alive
    ppd = ppd[ppd['PRESUMED_DEAD_FLAG_2'] == 'None']

    #Define subset of DOs
    sub_ppd = ppd[ppd.TOP_CD == 20]

    return(ppd, sub_ppd)

#Total
def get_total_table(ppd_df):
    '''Get complete counts'''
    all_deliverable = ppd_df[ppd_df['ADDRESS_UNDELIVERABLE_FLAG_2'] == 'None']
    counts = ppd_df.count()
    fax_count = counts['FAX_NUMBER']
    polo_count = counts['POLO_MAILING_LINE_2']
    telephone_count = counts['TELEPHONE_NUMBER']
    # no_delivery_count = counts['ADDRESS_UNDELIVERABLE_FLAG']
    all_mailing = counts['MAILING_LINE_2']
    deliverable_counts = all_deliverable.count()
    mailing_address_count = deliverable_counts['MAILING_LINE_2']
    deliverable_home = len(all_deliverable[all_deliverable.ADDRESS_TYPE.isin([2, 3])])
    deliverable_office = len(all_deliverable[all_deliverable.ADDRESS_TYPE == 1])
    top_count = len(ppd_df[ppd_df['TOP_CD'] != 100])
    pe_cd_count = len(ppd_df[ppd_df['PE_CD'] != 110])
    prim_spec_count = len(ppd_df[ppd_df['PRIM_SPEC_CD'] != 'US'])
    total_records = len(ppd_df)

    value_dict = {
        'totalrecords':total_records,
        'mailingaddress':mailing_address_count,
        'polo':polo_count,
        'telephone':telephone_count,
        'faxnumber':fax_count,
        'top':top_count,
        'pe':pe_cd_count,
        'primspec':prim_spec_count,
        'allmailing': all_mailing,
        'deliverable_home': deliverable_home,
        'deliverable_office': deliverable_office
    }
    print(value_dict)
    transposed = pd.DataFrame(value_dict, ['Count']).transpose()

    return transposed

def get_wslive_results(wslive_file_location):
    '''Read WSLive Results'''
    wslive_table = pd.read_excel(wslive_file_location, sheet_name='Summary Percentage', header=3)
    values = list(wslive_table[wslive_table['POLO Address Status'] == 'Confirmed'].iloc[:, -3])
    print(values)
    cleaned_values = [x for x in values if (np.isnan(x) == False)]
    # cleaned_values.pop(5)
    # cleaned_values.pop(4)
    # cleaned_values.pop(1)
    print(cleaned_values)

    col_list = ['polo_correct',
                'telephone_correct',
                'telephone_2_correct']

    wslive_df = pd.DataFrame({'1':col_list, '2':cleaned_values})
    print(wslive_df)

    return wslive_df

def read_old_scorecard(old_scorecard_location):
    '''Read old scorecard'''
    notes = pd.read_excel(old_scorecard_location, sheet_name='Notes')
    notes_2 = pd.read_excel(old_scorecard_location, sheet_name='Notes_2')
    notes_3 = pd.read_excel(old_scorecard_location, sheet_name='Notes_3')

    return(notes, notes_2, notes_3)

def get_notes(total, sub, correct, email, physicians, students):
    '''Get notes'''
    totalrecords = int(total.loc['totalrecords'])
    mailingaddress = int(total.loc['mailingaddress'])
    polo = int(total.loc['polo'])
    telephone = int(total.loc['telephone'])
    faxnumber = int(total.loc['faxnumber'])
    top = int(total.loc['top'])
    pe = int(total.loc['pe'])
    primspec = int(total.loc['primspec'])
    all_mailing = int(total.loc['allmailing'])
    deliverable_home = int(total.loc['deliverable_home'])
    deliverable_office = int(total.loc['deliverable_office'])

    totalrecords_dpc = int(sub.loc['totalrecords'])
    mailingaddress_dpc = int(sub.loc['mailingaddress'])
    polo_dpc = int(sub.loc['polo'])
    telephone_dpc = int(sub.loc['telephone'])
    faxnumber_dpc = int(sub.loc['faxnumber'])
    top_dpc = int(sub.loc['top'])
    pe_dpc = int(sub.loc['pe'])
    primspec_dpc = int(sub.loc['primspec'])

    polo_correctness = float(correct.iloc[0, 1])
    phone_correctness = float(correct.iloc[1, 1])
    phone_2_correctness = float(correct.iloc[2, 1])

    email_count = get_email_data(email)[0]
    email_correctness = get_email_data(email)[1]

    mailing_completeness = mailingaddress/totalrecords
    polo_completeness = polo_dpc/totalrecords_dpc
    phone_completeness = telephone_dpc/totalrecords_dpc
    fax_completeness = faxnumber_dpc/totalrecords_dpc
    practice_compelteness = top/totalrecords
    employment_completeness = pe/totalrecords
    spec_completeness = primspec/totalrecords
    email_completeness = email_count/totalrecords

    polo_combo = polo_correctness * polo_completeness
    phone_combo = phone_correctness * phone_completeness
    phone_2_combo = phone_2_correctness * phone_completeness
    email_combo = email_correctness * email_completeness

    polo_correct = int(polo_combo * totalrecords_dpc)
    phone_correct = int(phone_combo * totalrecords_dpc)
    phone_2_correct = int(phone_2_combo * totalrecords_dpc)
    email_corect = int(email_combo * totalrecords)

    do_student = students
    do_physician = physicians
    do_student_total = int(30367)
    do_physician_total = int(121006)
    do_student_complete = do_student/do_student_total
    do_physician_complete = do_physician/do_physician_total
    
    all_ = f'All Physicians: {"{:,}".format(totalrecords)} Records'
    all_dpc = f'Direct Patient Care (DPC): {"{:,}".format(totalrecords_dpc)} Records'

    today_date = datetime.today()
    last_year = (today_date - relativedelta(months=1, years=1)).strftime("%B" " " "%Y")
    two_year = (today_date - relativedelta(months=1, years=2)).strftime("%B" " " "%Y")
    last_month = (today_date - relativedelta(months=1)).strftime("%B" " " "%Y")
    month = f'Cumulative Change from {last_year}'
    month_2 = f'Cumulative Change from {two_year}'
    month_3 = f'Change from {last_month}'
    do_not_contact = 30030

    notes_list_ = [totalrecords,
                   mailingaddress,
                   polo,
                   telephone,
                   faxnumber,
                   top,
                   pe,
                   primspec,
                   email_count,
                   totalrecords_dpc,
                   mailingaddress_dpc,
                   polo_dpc,
                   telephone_dpc,
                   faxnumber_dpc,
                   top_dpc,
                   pe_dpc,
                   primspec_dpc,
                   polo_correctness,
                   phone_correctness,
                   phone_2_correctness,
                   email_correctness,
                   do_student,
                   do_physician,
                   do_student_total,
                   do_physician_total,
                   all_,
                   all_dpc,
                   month,
                   month_2,
                   month_3,
                   all_mailing,
                   deliverable_home,
                   deliverable_office,
                   do_not_contact
                   ]
    notes_2_list_ = [mailing_completeness,
                     polo_completeness,
                     phone_completeness,
                     fax_completeness,
                     practice_compelteness,
                     employment_completeness,
                     spec_completeness,
                     email_completeness,
                     polo_correctness,
                     phone_correctness,
                     phone_2_correctness,
                     email_correctness,
                     polo_correct,
                     phone_correct,
                     phone_2_correct,
                     email_corect,
                     polo_combo,
                     phone_combo,
                     phone_2_combo,
                     email_combo,
                     do_student_complete,
                     do_physician_complete,
                     totalrecords,
                     totalrecords_dpc]

    NOTE_1 = pd.DataFrame(notes_list_)
    NOTE_2 = pd.DataFrame(notes_2_list_)
    return (NOTE_1, NOTE_2)

def get_dates():
    '''Get relevant dates'''
    today_date = datetime.today()
    scorecard_month = (today_date - relativedelta(months=1)).strftime("%b" " " "%Y")
    last_year = (today_date - relativedelta(months=1, years=1)).strftime("%b" " " "%Y")
    last_year_one = (today_date - relativedelta(months=2, years=1)).strftime("%b" " " "%Y")
    two_year = (today_date - relativedelta(months=2, years=2)).strftime("%b" " " "%Y")
    return(scorecard_month, last_year, last_year_one, two_year)

def get_new_notes(notes_list, notes_2_list, notes, notes_2, notes_3):
    '''Get new notes'''
    scorecard_month, last_year, last_year_one, two_year = get_dates()
    notes.COL1 = notes_list
    notes_3[last_year] = list(notes_2[last_year])
    notes_3 = notes_3.drop(columns=two_year)

    notes_2 = notes_2.drop(columns=last_year_one)
    notes_2[scorecard_month] = notes_2_list
    print(len(notes_2))
    standard_devs = []
    for num in list(range(0, 24)):
        standard_devs.append(np.std(notes_2.iloc[[num], 2:15].values, dtype=np.float64))
    print(len(standard_devs))
    notes_2.Standard_Deviation = standard_devs
    return(notes, notes_2, notes_3)

def main():  
    local_directory = 'C:/Users/vigrose/Data/Scorecard'
    print('Grabbing file names...')
    ppd_file = newest(local_directory, 'ppd_data')
    wslive_file = newest(local_directory, 'WSLive')
    old_scorecard = newest(local_directory, 'Masterfile-Scorecard')
    print(old_scorecard)
    email_file = newest(local_directory, 'Email')
    do_file = newest(local_directory, 'do_count')
    print('Reading ppd...')
    ppd, sub_ppd = read_ppd(ppd_file)
    print('Getting ppd data...')
    total = get_total_table(ppd)
    sub = get_total_table(sub_ppd)
    print('Getting wslive data...')
    correct = get_wslive_results(wslive_file)
    print('Reading old scorecard...')
    notes, notes_2, notes_3 = read_old_scorecard(old_scorecard)
    print('Getting DO counts...')
    physicians, students = get_do_counts(do_file)
    print('Getting new notes...')
    note_list, note_list_2 = get_notes(total, sub, correct, email_file, physicians, students)
    print('Editing notes...')
    new_notes, new_notes_2, new_notes_3 = get_new_notes(note_list, note_list_2, notes, notes_2, notes_3)
    print('Writing to file...')
    with pd.ExcelWriter(f'{local_directory}/output_2.xlsx') as writer:  
        new_notes.to_excel(writer, sheet_name='Notes', index=False)
        new_notes_2.to_excel(writer, sheet_name='Notes_2', index=False)
        new_notes_3.to_excel(writer, sheet_name='Notes_3', index=False)

if __name__ == "__main__":
    main()
