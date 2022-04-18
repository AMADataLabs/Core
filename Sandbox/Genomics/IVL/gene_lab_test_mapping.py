import xml.etree.ElementTree as ET
import pandas as pd
from pandas import DataFrame
from lxml import etree

events = ("start","end")
context = etree.iterparse(r"C:\Users\Animesh\Desktop\IVL\gtr_ftp\gtr_ftp.xml", tag='GTRLabData')
GTR_data = {}
final_list = []
final_list2 = []
for event, elem in context:
    for child in elem:
        if child.tag == 'GTRLab':
            GTR_data['GTRLab_ID'] = child.attrib['id']
            gene_list = []
            gene_symbol = []
            test_id = []
            gene_test_xref = []
            c += 1
            if len(child.findall('GeneTesting')) > 0:
                gene = child.findall('GeneTesting')
                for gene_id in gene:
                    gene_list.append(gene_id.attrib['GeneID'])
                    gene_symbol.append(gene_id.find('GeneSymbol').text)
                GTR_data['GeneID'] = gene_list
                GTR_data['GeneSymbol'] = gene_symbol
            else:
                GTR_data['GeneID'] = 'None'
                GTR_data['GeneSymbol'] = 'None'
        if child.tag == 'GTRLabTest':
            test_id.append(child.attrib['id'])
            if child.find('ClinVarSet').find('ClinVarAssertion').find('MeasureSet').find('Measure').attrib['Type'] == 'Gene':
                try:
                    gene_test_xref.append(child.find('ClinVarSet').find('ClinVarAssertion').find('MeasureSet').find('Measure').find('XRef').attrib['ID'])
                except:
                    gene_test_xref.append('0')
            else:
                gene_test_xref.append('None')
            GTR_data['LabTestID'] = test_id
            GTR_data['Gene_Test_Xref'] = gene_test_xref
    print(GTR_data)
    gene_data = list([GTR_data['GTRLab_ID'], GTR_data['GeneID'], GTR_data['GeneSymbol']])
    lab_test_data = list([GTR_data['GTRLab_ID'], GTR_data['LabTestID'], GTR_data['Gene_Test_Xref']])
    #pf = list(GTR_data.values())
    final_list.append(gene_data)
    final_list2.append(lab_test_data)

    elem.clear()
#print(final_list)
#print(final_list2)

df_gene = pd.DataFrame(final_list, columns=['GTRLab_ID', 'GeneID', 'GeneSymbol'])
df2_gene = df_gene.set_index(['GTRLab_ID']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop(
    ['level_1'], 1)
df_lab_test = pd.DataFrame(final_list2, columns=['GTRLab_ID', 'GTRLabTest_ID', 'GeneID'])
df2_lab_test = df_lab_test.set_index(['GTRLab_ID']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop(
    ['level_1'], 1)
#print(df2_gene)
#print(df2_lab_test)
df_final = pd.merge(df2_gene, df2_lab_test, on = ['GTRLab_ID', 'GeneID'], how = 'outer')

print(df_final)

df_final.to_csv(r'C:\Users\Animesh\Desktop\IVL\GTR_data\Gene_LabTest_Mapping', index=False, na_rep = 'None')