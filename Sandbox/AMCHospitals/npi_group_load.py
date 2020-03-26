'''
This script grabs group entity subset of NPI file
'''
#Import dependencies
from datetime import date
import os
import pandas as pd

#Set today
TODAY = str(date.today())

#Set file locations
NPI_FILE_LOCATION = os.getenv('NPI_FILE_RAW')
NPI_RESULTS_FOLDER = os.getenv('NPI_FILTERED_FOLDER')

#Make empty df
GROUP_NPI_DF = pd.DataFrame([{}])

#Chunk and filter NPI
try:
    COUNT = 0
    for gm_chunk in pd.read_csv(NPI_FILE_LOCATION, engine='python', encoding='utf-8',
                                error_bad_lines=False, chunksize=10000):
        tbl = gm_chunk[gm_chunk['Entity Type Code'] == 2]
        GROUP_NPI_DF = pd.concat([GROUP_NPI_DF, tbl], sort=True)
        count += 1
        print(f'{count} chunks down')
        print(f'{len(GROUP_NPI_DF)} total rows')

    #Rename columns
    GROUP_NPI_DF.columns = [c.upper() for c in GROUP_NPI_DF.columns.values]
    GROUP_NPI_DF.columns = [c.replace(' ', '_') for c in GROUP_NPI_DF.columns.values]
    GROUP_NPI_DF = GROUP_NPI_DF.rename(columns={
        'PROVIDER_ORGANIZATION_NAME_LEGAL_BUSINESS_NAME':'PROVIDER_ORGANIZATION_NAME__LEGAL_BUSINESS_NAME'
        })
    #Save to csv
    GROUP_NPI_DF[0:1000000].to_csv(f'{NPI_RESULTS_FOLDER}Group_Entities_{TODAY}.csv', index=False)
    GROUP_NPI_DF[1000000:].to_csv(f'{NPI_RESULTS_FOLDER}Group_Entities{TODAY}.csv', index=False)

except (KeyboardInterrupt, SystemExit):
    #Rename columns
    GROUP_NPI_DF.columns = [c.upper() for c in GROUP_NPI_DF.columns.values]
    GROUP_NPI_DF.columns = [c.replace(' ', '_') for c in GROUP_NPI_DF.columns.values]
    GROUP_NPI_DF = GROUP_NPI_DF.rename(columns={
        'PROVIDER_ORGANIZATION_NAME_LEGAL_BUSINESS_NAME':'PROVIDER_ORGANIZATION_NAME__LEGAL_BUSINESS_NAME'
        })

    #Save to csv
    GROUP_NPI_DF[0:1000000].to_csv(f'{NPI_RESULTS_FOLDER}_Group_Entities_{TODAY}.csv', index=False)
    GROUP_NPI_DF[1000000:].to_csv(f'{NPI_RESULTS_FOLDER}_Group_Entities{TODAY}.csv', index=False)
    raise
