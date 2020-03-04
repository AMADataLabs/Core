'''
This script grabs group entity subset of NPI file
'''
#Import dependencies
from datetime import date
from tkinter import filedialog
import pandas as pd

#Set today
today = str(date.today())

#Set file locations
npi_file_location = filedialog.askopenfilename(initialdir="F:\\",
                                               title="Choose the npi file to use...")
npi_results_folder = filedialog.askdirectory(initialdir="F:\\",
                                             title="Choose the folder to save results to..")

#Make empty df
group_npi_df = pd.DataFrame([{}])

#Chunk and filter NPI
try:
    count = 0
    for gm_chunk in pd.read_csv(npi_file_location, engine='python', encoding='utf-8',
                                error_bad_lines=False, chunksize=10000):
        tbl = gm_chunk[gm_chunk['Entity Type Code'] == 2]
        group_npi_df = pd.concat([group_npi_df, tbl], sort=True)
        count += 1
        print(f'{count} chunks down')
        print(f'{len(group_npi_df)} total rows')

    #Rename columns
    group_npi_df.columns = [c.upper() for c in group_npi_df.columns.values]
    group_npi_df.columns = [c.replace(' ', '_') for c in group_npi_df.columns.values]
    group_npi_df = group_npi_df.rename(columns={
        'PROVIDER_ORGANIZATION_NAME_LEGAL_BUSINESS_NAME':'PROVIDER_ORGANIZATION_NAME__LEGAL_BUSINESS_NAME'
        })
    #Save to csv
    group_npi_df[0:1000000].to_csv(f'{npi_results_folder}Group_Entities_{today}.csv', index=False)
    group_npi_df[1000000:].to_csv(f'{npi_results_folder}Group_Entities{today}.csv', index=False)

except (KeyboardInterrupt, SystemExit):
    #Rename columns
    group_npi_df.columns = [c.upper() for c in group_npi_df.columns.values]
    group_npi_df.columns = [c.replace(' ', '_') for c in group_npi_df.columns.values]
    group_npi_df = group_npi_df.rename(columns={
        'PROVIDER_ORGANIZATION_NAME_LEGAL_BUSINESS_NAME':'PROVIDER_ORGANIZATION_NAME__LEGAL_BUSINESS_NAME'
        })

    #Save to csv
    group_npi_df[0:1000000].to_csv(f'{npi_results_folder}_Group_Entities_{today}.csv', index=False)
    group_npi_df[1000000:].to_csv(f'{npi_results_folder}_Group_Entities{today}.csv', index=False)
    raise
