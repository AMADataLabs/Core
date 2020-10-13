#GTR_Data_XML_parsing_code:-

#Condition/Phenotype Master

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

            clinVarSet = child.find('ClinVarSet').findall('ClinVarAssertion')
            for clinVarAssert in clinVarSet:
                traitset = clinVarAssert.find('TraitSet').findall('Trait')
                for trait in traitset:
                    GTR_data['ConditionDescription'] = trait.find('Name').text
                    xref = trait.findall('XRef')
                    for att in xref:
                        if att.attrib['DB'] == 'MedGen':
                            GTR_data['Condition_ID'] = att.attrib['ID']
                            GTR_data['TestCount'] = 1
                            print(GTR_data)
                            pf = list(GTR_data.values())
                            final_list.append(pf)
    elem.clear()

print(final_list)
df1 = pd.DataFrame(final_list, columns=['GTRLabTestConditionDescription', 'GTRLabTestCondition_ID', 'TestCount'])
df1 = df1.groupby(["GTRLabTestConditionDescription", "GTRLabTestCondition_ID"])['TestCount'].sum().reset_index()
#df2 = df1.set_index(['GTRLabTest_ID']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop('level_1', 1)
print(df1)

df1.to_csv(r'C:\Users\Animesh\Desktop\IVL\GTR_data\GTR_ConditionMaster.csv', index=False, na_rep='None')