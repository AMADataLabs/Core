'''
This script compiles some statistics about medscape data
'''
import os
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

TODAY = str(date.today())

DIRECTORY = 'U:/Source Files/Data Analytics/Data-Science/Data/Medscape/'

def newest(path, text):
    '''Grabs newest filename'''
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if text in basename]
    return max(paths, key=os.path.getctime)

US_RESULTS = newest(DIRECTORY, 'USA_ME')
ALL_RESULTS = newest(DIRECTORY, 'm_2')

US_DATA = pd.read_csv(US_RESULTS)
ALL_DATA = pd.read_csv(ALL_RESULTS)

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
                                title='COVID-19 Healthcare Worker Fatalities by Role - USA',
                                color='darkorchid')
    age_df = pd.DataFrame({'Age':['80 and older', '70-79', '60-69', '50-59', '40-49', '30-39',
                                  'under 30', 'Unknown'], 'Count':[eight, seven, six, five, four,
                                                                   three, two, unk]})
    return(role_df, role_plt, age_df)
#Roles
ROLE_DF, ROLE_PLT, AGE_DF = get_counts(US_DATA)
plt.savefig(f'{DIRECTORY}ROLE_{TODAY}.png')
plt.close()
#State breakdown
STATE_DF = US_DATA.groupby('STATE').count()['NAME'].sort_values(ascending=False)
STATE_PLT = STATE_DF.plot.bar(title='COVID-19 Healthcare Worker Fatalities by State - USA',
                              color='darkorchid', figsize=(15, 10), rot=45, legend=False)
plt.savefig(f'{DIRECTORY}STATE_{TODAY}.png')
plt.close()
#Country breakdown
COUNTRY_DF = ALL_DATA.groupby('COUNTRY').count()['NAME'].sort_values(ascending=False)
COUNTRY_PLT = COUNTRY_DF.plot.bar(title='COVID-19 Healthcare Worker Fatalities by Country',
                                  color='darkorchid', figsize=(15, 10), rot=45, legend=False)
plt.savefig(f'{DIRECTORY}COUNTRY_{TODAY}.png')
plt.close()
#Age breakdown
AGE_DF_2 = US_DATA[(US_DATA.AGE != 'age unknown')&(US_DATA.AGE != 'None')][['NAME', 'AGE']]
AGE_DF_2['AGE'] = AGE_DF_2.AGE.astype(int)
AGE_PLT = AGE_DF_2.hist(color='darkorchid')
plt.savefig(f'{DIRECTORY}AGE_{TODAY}.png')
plt.close()
with pd.ExcelWriter(f'{DIRECTORY}USA_Stats_{TODAY}.xlsx') as writer:
    STATE_DF.to_excel(writer, sheet_name='By State - USA')
    ROLE_DF.to_excel(writer, sheet_name='By Role - USA', index=False)
    AGE_DF.to_excel(writer, sheet_name='By Age - USA', index=False)
    COUNTRY_DF.to_excel(writer, sheet_name='By Country')
