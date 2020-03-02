import pandas as pd
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(initialdir = "C:\\",
                                         title = "Choose DHC combined file...")

out_dir = filedialog.askdirectory(initialdir = "C:\\",
                                         title = "Choose directory to save in...")

out_dir = out_dir.replace("/", "\\")
out_dir += "\\"

out_name = str(input("Enter the name of the output count file: "))
out_file = out_dir + out_name
if '.xlsx' not in out_file:
    ext_ndx = out_file.find('.')
    if ext_ndx < 0:
        out_file += '.xlsx'
    else:
        out_file = out_file[:ext_ndx] + '.xlsx'


DHC_df = pd.read_csv(file_path, delimiter = ",", index_col = None, header = 0)

col_names = DHC_df.columns.values

# Convert # of Physicians in PG (Largest Affiliation) to a number
DHC_df = DHC_df[DHC_df['# of Physicians in PG (Largest Affiliation)'] !=  ' 1 Group Members)"']
DHC_df['# of Physicians in PG (Largest Affiliation)'] = \
       DHC_df['# of Physicians in PG (Largest Affiliation)'].astype('str')  
DHC_df['# of Physicians in PG (Largest Affiliation)'] = \
       DHC_df['# of Physicians in PG (Largest Affiliation)'].str.replace(',', '')                     
DHC_df['# of Physicians in PG (Largest Affiliation)'] = \
       DHC_df['# of Physicians in PG (Largest Affiliation)'].astype('float')  

# Make all string entries uppercase
for name in col_names:
    if str(DHC_df[name].dtype) == 'object' or str(DHC_df[name].dtype) == 'str':
        DHC_df[name] = DHC_df[name].astype('str')  
        DHC_df[name] = DHC_df[name].str.upper()

# Filter out US territories (Guam, Puerto Rico)
DHC_df = DHC_df[DHC_df['State'] != 'GU']
DHC_df = DHC_df[DHC_df['State'] != 'PR']

# Generate counts including Do Not Call Registry
total_count = DHC_df.shape[0]

num_tot_addr = sum(DHC_df['Address'] != 'NAN')
num_tot_phone = sum(DHC_df['Phone Number'] != 'NAN')
num_tot_fax = sum(DHC_df['Fax Number'] != 'NAN')
num_tot_spec = sum(DHC_df['Primary Specialty'] != 'NAN')
num_tot_email = sum(DHC_df['Email'] != 'NAN')

tot_values = [total_count, num_tot_addr, num_tot_phone, num_tot_fax, num_tot_spec,
                           num_tot_email]
tot_desc = ['total_count', 'num_tot_addr', 'num_tot_phone', 
                                        'num_tot_fax', 'num_tot_spec', 'num_tot_email']
tot_out_df = pd.DataFrame(tot_desc, columns = ['description'])
tot_out_df['counts'] = tot_values

writer = pd.ExcelWriter(out_file, engine='xlsxwriter')
tot_out_df.to_excel(writer, sheet_name = 'Total_Counts')


# Filter out any Do Not Call registered - same as our No Contact
DHC_filtered_df = DHC_df[DHC_df['Do Not Call Registry'] != 'REGISTERED']

# Generate counts excluding Do Not Call Registry
filter_count = DHC_filtered_df.shape[0]

num_filt_addr = sum(DHC_filtered_df['Address'] != 'NAN')
num_filt_phone = sum(DHC_filtered_df['Phone Number'] != 'NAN')
num_filt_email = sum(DHC_filtered_df['Email'] != 'NAN')
num_filt_fax = sum(DHC_filtered_df['Fax Number'] != 'NAN')
num_filt_spec = sum(DHC_filtered_df['Primary Specialty'] != 'NAN')

filt_values = [filter_count, num_filt_addr, num_filt_phone, num_filt_fax, num_filt_spec,
                           num_filt_email]
filt_desc = ['total_count', 'num_tot_addr', 'num_tot_phone', 
                                        'num_tot_fax', 'num_tot_spec', 'num_tot_email']
filt_out_df = pd.DataFrame(filt_desc, columns = ['description'])
filt_out_df['counts'] = filt_values

filt_out_df.to_excel(writer, sheet_name = 'Exlude_No_Call_Counts')
writer.save()



