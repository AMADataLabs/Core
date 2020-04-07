'''
This script compiles some statistics about medscape data
'''
import os
from datetime import datetime
import pandas as pd

TODAY = str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '')

DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Medscape/'

def newest(path):
    '''Grabs newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if 'USA_ME' in basename]
    return max(paths, key=os.path.getctime)

RESULT_DIR = newest(DIRECTORY)
print(RESULT_DIR)
DATA = pd.read_csv(RESULT_DIR)

def get_counts(dataframe):
    '''GET COUNTS'''
    nurse = 0
    tech = 0
    assistant = 0
    admin = 0
    other = 0
    phys = 0
    eight = 0
    seven = 0
    six = 0
    five = 0
    four = 0
    three = 0
    two = 0
    unk = 0

    for row in dataframe.itertuples():
        if 'Nurse' in row.SPECIALTY:
            nurse += 1
        elif 'Tech' in row.SPECIALTY:
            tech += 1
        elif 'Assistant' in row.SPECIALTY:
            assistant += 1
        elif 'Admin' in row.SPECIALTY:
            admin += 1
        elif row.ME != 'None':
            phys += 1
        else:
            other += 1
        if row.AGE.isnumeric():
            age = int(row.AGE)
            if age >= 80:
                eight += 1
            elif age >= 70:
                seven += 1
            elif age >= 60:
                six += 1
            elif age >= 50:
                five += 1
            elif age >= 40:
                four += 1
            elif age >= 30:
                three += 1
            else:
                two += 1
        else:
            unk += 1
    role_df = pd.DataFrame({'Role':['Physician', 'Nurse', 'Technician', 'PA', 'Administration',
                                    'Other'], 'Count':[phys, nurse, tech, assistant, admin, other]})
    role_plt = role_df.plot.bar(x='Role', y='Count', rot=0,
                                title='COVID-19 Healthcare Worker Fatalities by Role',
                                color='darkorchid')
    age_df = pd.DataFrame({'Age':['80 and older', '70-79', '60-69', '50-59', '40-49', '30-39',
                                  'under 30', 'Unknown'], 'Count':[eight, seven, six, five, four,
                                                                   three, two, unk]})
    age_plt = age_df.plot.bar(x='Age', y='Count', rot=0,
                              title='COVID-19 Healthcare Worker Fatalities by Age',
                              color='darkorchid')
    return(role_df, role_plt, age_df, age_plt)

ROLE_DF, ROLE_PLT, AGE_DF, AGE_PLT = get_counts(DATA)
STATE_DF = DATA.groupby('STATE').count()['NAME']
STATE_PLT = STATE_DF.plot.bar(title='COVID-19 Healthcare Worker Fatalities by State',
                              color='darkorchid')

with pd.ExcelWriter(f'{DIRECTORY}USA_Stats_{TODAY}.xlsx') as writer:
    STATE_DF.to_excel(writer, sheet_name='By State')
    ROLE_DF.to_excel(writer, sheet_name='By Role', index=False)
    AGE_DF.to_excel(writer, sheet_name='By Age', index=False)

FIG_1 = AGE_PLT.get_figure()
FIG_1.savefig(f'{DIRECTORY}AGE_{TODAY}.png')
FIG_2 = ROLE_PLT.get_figure()
FIG_2.savefig(f'{DIRECTORY}ROLE_{TODAY}.png')
FIG_3 = STATE_PLT.get_figure()
FIG_3.savefig(f'{DIRECTORY}STATE_{TODAY}.png')
