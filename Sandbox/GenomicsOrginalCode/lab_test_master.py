# GTR_Data_XML_parsing_code:-

# LabTestMaster

import xml.etree.ElementTree as ET
import pandas as pd
from pandas import DataFrame
from pandas._libs.reshape import explode

events = ("start", "end")
tree = ET.parse(r"C:\Users\Animesh\Desktop\IVL\gtr_ftp\GTR_xml_data_sample")  # sets up iterparse with labdata tags as root elements

GTR_data = {}
final_list = []

root = tree.getroot()
#l = [elem.tag for elem in root.iter()]

for gtrLab in root.iter('GTRLabData'):
    GTR_data['GtrLab_id'] = gtrLab.find('GTRLab').attrib['id']

    for gtr in gtrLab.iter('GTRLabTest'):
        test_comment = []
        GTR_data['Test_ID'] = gtr.attrib['id']

        try:
            GTR_data['testname'] = gtr.find('TestName').text
        except:
            GTR_data['testname'] = gtr.find('TestName').text

        try:
            GTR_data['testshortname'] = gtr.find('TestShortName').text
        except:
            GTR_data['testshortname'] = 'None'

        try:
            GTR_data['manufacturertestname'] = gtr.find('ManufacturerTestName').text
        except:
            GTR_data['manufacturertestname'] = 'None'

        try:
            GTR_data['gtraccession'] = gtr.attrib['GTRAccession'] + '.' + gtr.attrib['Version']
        except:
            GTR_data['gtraccession'] = 'None'

        print(GTR_data)
        pf = list(GTR_data.values())
        final_list.append(pf)

# print(final_list)
df1 = pd.DataFrame(final_list, columns=['GTRLab_ID', 'GTRLabTest_ID', 'GTRLabTestName', 'GTRLabTestShortName',
                                        'GTRManufacturerTestName', 'GTRAccession'])
print(df1)
df1.to_csv(r'C:\Users\Animesh\Desktop\IVL\GTR_data\GTR_LabTestMaster.csv', index=False, na_rep='None')