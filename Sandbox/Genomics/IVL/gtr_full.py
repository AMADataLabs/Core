import xml.etree.ElementTree as ET
import pandas as pd
from pandas import DataFrame
from lxml import etree



events = ("start", "end")
context = etree.iterparse(r"F:\Swagat\IVL\gtr_ftp\gtr_ftp.xml", tag='GTRLabData')
GTR_data = {}
#final_list = []
df1 = pd.DataFrame()
for event, elem in context:
	final_list = []
	for child in elem:

		if child.tag == 'GTRLab':
			gene_list = []
			testname = []
			testshortname = []
			manufacturertestname = []
			gtraccession = []

			GTR_data['GtrLab_id'] = child.attrib['id']

			try:
				GTR_data['LabName'] = child.find('Organization').find('Name').text
			except:
				GTR_data['LabName'] = 'None'

			try:
				GTR_data['Country'] = child.find('Organization').find('MailingAddress').find('Country').text
			except:
				GTR_data['Country'] = 'None'

		if child.tag == 'GTRLabTest':
			GTR_data['Test_ID'] = child.attrib['id']
			GTR_data['gene_symbol'] = 'None'
			GTR_data['gene_id'] = 'None'

			method_category = []
			testmethod = []
			specimentype = []
			testcomment = []
			condition_desc = []
			condition_id = []

			try:
				clinVarSet = child.find('ClinVarSet').findall('ClinVarAssertion')
				for clinVarAssert in clinVarSet:
					measureset = clinVarAssert.findall('MeasureSet')
					for measure in measureset:
						if measure.find('Measure').attrib['Type'] == 'Gene':
							GTR_data['gene_symbol'] = measure.find('Measure').find('Symbol').text

						gene_xref = measure.find('Measure').findall('XRef')
						for gene in gene_xref:
							if gene.attrib['DB'] == 'Gene':
								GTR_data['gene_id'] = gene.attrib['ID']
			except:
				GTR_data['gene_symbol'] = 'None'
				GTR_data['gene_id'] = 'None'

			try:
				GTR_data['LabTestName'] = child.find('TestName').text
			except:
				GTR_data['LabTestName'] = 'None'

			try:
				GTR_data['TestShortName'] = child.find('TestShortName').text
			except:
				GTR_data['TestShortName'] = 'None'

			try:
				GTR_data['manufacturertestname'] = child.find('ManufacturerTestName').text
			except:
				GTR_data['manufacturertestname'] = 'None'

			category = child.find('Method').find('TopCategory').findall('Category')
			if len(category) == 0:
				method_category.append('None')
				testmethod.append('None')
			else:
				for c in category:
					method_category.append(c.attrib['Value'])
					testmethod.append(c.find('Methodology').attrib['Value'])
			GTR_data['MethodCategory'] = method_category
			GTR_data['TestMethod'] = testmethod

			try:
				clinVarSet = child.find('ClinVarSet').findall('ClinVarAssertion')
				for clinVarAssert in clinVarSet:
					traitset = clinVarAssert.find('TraitSet').findall('Trait')
					for trait in traitset:
						condition_desc.append(trait.find('Name').text)
						xref = trait.findall('XRef')
						for att in xref:
							if att.attrib['DB'] == 'MedGen':
								condition_id.append(att.attrib['ID'])
			except:
				condition_desc.append('None')
				condition_id.append('None')
			GTR_data['GTRLabTestConditionDescription'] = condition_desc
			GTR_data['GTRLabTestCondition_ID'] = condition_id

			print(GTR_data)

			pf = list(GTR_data.values())

			final_list.append(pf)
			#print(final_list)
	df = pd.DataFrame(final_list, columns=['GTRLab_ID', 'GTRLabName', 'GTRLabCountryName', 'GTRLabTest_ID', 'GeneSymbol',
											   'GeneID', 'GTRLabTestName', 'GTRLabTestShortName', 'GTRManufacturerTestName',
											'MethodCategory', 'TestMethod', 'GTRLabTestConditionDescription', 'GTRLabTestCondition_ID'])
	df = df.set_index(['GTRLab_ID', 'GTRLabName', 'GTRLabCountryName', 'GTRLabTest_ID', 'GeneSymbol', 'GeneID', 'GTRLabTestName', 'GTRLabTestShortName', 'GTRManufacturerTestName']).apply(lambda x: x.apply(pd.Series).stack()).reset_index()#.drop('level_9', 1)
	df1 = df1.append(df, ignore_index=True)#.drop_duplicates()
	df1 = df1.ffill(axis=0)
	#print(df1)
	elem.clear()







#df = df.set_index(['GTRLab_ID', 'GTRLabName', 'GTRLabCountryName', 'GTRLabTest_ID', 'GeneSymbol', 'GeneID', 'GTRLabTestName',
					  # 'GTRLabTestShortName', 'GTRManufacturerTestName']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop('level_9', 1)





df1 = df1.drop('level_9', 1)
df1.to_csv(r"F:\Swagat\IVL\GTR_data\GTR_full_data_exploded.csv", index=False)
#df.to_parquet(r'C:\Users\Animesh\Desktop\IVL\GTR_data\GTR_full_data_method_exploded.parquet', engine = 'auto', compression='snappy', index=False)