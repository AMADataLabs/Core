#GTR_Data_XML_parsing_code:-

#LabMaster


import xml.etree.ElementTree as ET
import pandas as pd
from pandas import DataFrame
from pandas._libs.reshape import explode

events = ("start","end")
tree = ET.parse(r"C:\Users\Animesh\Desktop\IVL\gtr_ftp.xml\GTR_xml_data_sample") # sets up iterparse with labdata tags as root elements

GTR_data = {}
final_list = []

root = tree.getroot()
#l = [elem.tag for elem in root.iter()]

for gtrLab in root.iter('GTRLabData'):
    GTR_data['GtrLab_id'] = gtrLab.find('GTRLab').attrib['id']

    GTR_data['LabName'] = gtrLab.find('GTRLab').find('Organization').find('Name').text

    try:
        GTR_data['LabContact_Email'] = gtrLab.find('GTRLab').find('Organization').find('LabContact').find('Email').text
    except:
        GTR_data['LabContact_Email'] = 'None'

    try:
        GTR_data['LabContact_Phone'] = gtrLab.find('GTRLab').find('Organization').find('LabContact').find('Phone').text
    except:
        GTR_data['LabContact_Phone'] = 'None'

    try:
        GTR_data['LabContact_Fax'] = gtrLab.find('GTRLab').find('Organization').find('LabContact').find('Fax').text
    except:
        GTR_data['LabContact_Fax'] = 'None'

    try:
        GTR_data['LabContact_URL'] = gtrLab.find('GTRLab').find('Organization').find('LabContact').find('URL').text
    except:
        GTR_data['LabContact_URL'] = 'None'

    print(GTR_data)
    pf = list(GTR_data.values())
    final_list.append(pf)

# print(final_list)
df1 = pd.DataFrame(final_list, columns=['GTRLab_ID', 'GTRLabName', 'GTRLabContact_Email', 'GTRLabContact_Phone',
                                        'GTRLabContact_Fax', 'GTRLabContact_URL'])
df1.to_csv(r'C:\Users\Animesh\Desktop\IVL\GTR_data\GTR_LabMaster.csv', index=False, na_rep='None')