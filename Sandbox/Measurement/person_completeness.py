import measurement
import pandas as pd


methods_df = pd.read_excel('../../Data/Measurement/measurement_methods.xlsx')
path = '../../Data/Measurement/'
data_file = use.get_newest(path,'Person_Data')
data = pd.read_csv(data_file)
data.head()

#turn data into dictionary
person_data = data.to_dict('records')

complete_list = []
for row in person_data:
    complete_list+=measurement.measure(row, methods_df, 'COMPLETENESS')

pd.DataFrame(complete_list) 