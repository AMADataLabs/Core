import xml.etree.ElementTree as ET
import pandas as pd
from pandas import DataFrame
from lxml import etree

events = ("start","end")
context = etree.iterparse(r"C:\Users\Animesh\Desktop\IVL\gtr_ftp\gtr_ftp.xml", tag='GTRLabData')
GTR_data = {}
final_list = []
for event, elem in context:
    for child in elem:  # looking at deeper levels within each lab
        if child.tag == 'GTRLab':
            GTR_data['GTRLab_ID'] = child.attrib['id']
            GTR_data['']
            gene_id = []
            test_count = []
            gene_symbol = []
            for c in child:
                if c.tag == 'GeneTesting':
                    gene_id.append(c.attrib['GeneID'])
                    test_count.append(c.attrib['test_count'])
                    gene_symbol.append(c.find('GeneSymbol').text)
                    GTR_data['Gene_ID'] = gene_id
                    GTR_data['testCount'] = test_count
                    GTR_data['Gene_Symbol'] = gene_symbol

                else:
                    GTR_data['Gene_ID'] = 'None'
                    GTR_data['testCount'] = 0
                    GTR_data['Gene_Symbol'] = 'None'
                #else:
                 #   GTR_data['GeneID'] = 'None'
    print(GTR_data)
    pf = list(GTR_data.values())
    final_list.append(pf)
    elem.clear()
print(final_list)
df1 = pd.DataFrame(final_list, columns=['GTRLab_ID', 'GeneID', 'TestCount', 'GeneSymbol'])

# df1['index1'] = df1.index
df2 = df1.set_index(['GTRLab_ID']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop(
    ['level_1'], 1)
print(df2)
df2.to_csv(r'C:\Users\Animesh\Desktop\IVL\GTR_data\GeneMaster_FULL.csv', index=False, na_rep='None')