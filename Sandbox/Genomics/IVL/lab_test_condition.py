#GTR_Data_XML_parsing_code:-

#LabTestCondition/Phenotype

import xml.etree.ElementTree as ET
import pandas as pd
from lxml import etree
from pandas import DataFrame
from pandas._libs.reshape import explode

events = ("start","end")
context = etree.iterparse(r"C:\Users\Animesh\Desktop\IVL\gtr_ftp\gtr_ftp.xml", tag='GTRLabData')
GTR_data = {}
final_list = []
for event, elem in context:
    for child in elem:  # looking at deeper levels within each lab
        if child.tag == 'GTRLabTest':
            GTR_data['Test_ID'] = child.attrib['id']
            test_condition_ID = []

            clinVarSet = child.find('ClinVarSet').findall('ClinVarAssertion')
            for clinVarAssert in clinVarSet:
                traitset = clinVarAssert.find('TraitSet').findall('Trait')
                for trait in traitset:
                    xref = trait.findall('XRef')
                    for att in xref:
                        if att.attrib['DB'] == 'MedGen':
                            if att.attrib['ID'] not in test_condition_ID:
                                test_condition_ID.append(att.attrib['ID'])
            if len(test_condition_ID) == 0:
                GTR_data['Condition_ID'] = 'None'
            else:
                GTR_data['Condition_ID'] = test_condition_ID
        print(GTR_data)
        pf = list(GTR_data.values())
        final_list.append(pf)
        elem.clear()

# print(final_list)
df1 = pd.DataFrame(final_list, columns=['GTRLabTest_ID', 'GTRLabTestCondition_ID']).explode('GTRLabTestCondition_ID')
#df2 = df1.set_index(['GTRLabTest_ID']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop('level_1', 1)
#print(df1)

df1.to_csv(r'C:\Users\Animesh\Desktop\IVL\GTR_data\Condition_LabTest_Mapping.csv', index=False, na_rep='None')