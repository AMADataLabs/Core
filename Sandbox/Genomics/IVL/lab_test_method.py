import pandas as pd
import xml.etree.ElementTree as ET

GTR_data = {}
GTR_data['LabMethodID'] = 1000
final_list = []

def main():
    root = read_file()

    final_list = extract_data(root)

    df2 = create_dataframe_from_list(final_list)

    output_file(df2)


def read_file():
    tree = ET.parse(r"C:\Users\nkhatri\OneDrive - American Medical Association\Desktop\gtr_ftp.xml\gtr_ftp.xml")
    root = tree.getroot()

    return root

def extract_data(root):
    for gtrLab in root.iter('GTRLabData'):

        for gtr in gtrLab.iter('GTRLabTest'):

            method_category = []
            testmethod = []
            specimentype = []
            testcomment = []

            get_lab_test_id(gtr)

            increase_lab_method_id(gtr)

            category = get_category(gtr)

            get_method_category(category, method_category)

            get_test_method(category, testmethod)

            get_specimen_type(gtr, specimentype)

            get_test_comment(gtr, testcomment)

            appended_values = append_values_to_list(GTR_data)


    return appended_values


def get_lab_test_id(gtr):
    GTR_data['LabTest_ID'] = gtr.attrib['id']


def increase_lab_method_id(gtr):
    GTR_data['LabMethodID'] += 1


def get_category(gtr):
    category = gtr.find('Method').find('TopCategory').findall('Category')
    return category


def get_method_category(category, method_category):
    if len(category) == 1:
        GTR_data['MethodCategory'] = category[0].attrib['Value']
    else:
        for c in category:
            method_category.append(c.attrib['Value'])
        GTR_data['MethodCategory'] = method_category


def get_test_method(category, testmethod):
    if len(category) == 1:
        GTR_data['TestMethod'] = category[0].find('Methodology').attrib['Value']
    else:
        for c in category:
            testmethod.append(c.find('Methodology').attrib['Value'])
        GTR_data['TestMethod'] = testmethod


def get_specimen_type(gtr, specimentype):
    try:
        specimen = gtr.find('Specimen').findall('SpecimenType')
        if len(specimen) == 1:
            GTR_data['SpecimenType'] = specimen[0].text
        else:
            for spec in specimen:
                specimentype.append(spec.text)
                GTR_data['SpecimenType'] = specimentype
    except:
        GTR_data['SpecimenType'] = 'None'


def get_test_comment(gtr, testcomment):
    comment = gtr.findall('TestComment')
    if len(comment) > 0:
        if len(comment) == 1:
            GTR_data['TestComment'] = comment[0].text
        else:
            for com in comment:
                testcomment.append(com.text)
                GTR_data['TestComment'] = testcomment
    else:
        testcomment = 'None'
        GTR_data['TestComment'] = testcomment


def append_values_to_list(GTR_data):
    pf = list(GTR_data.values())
    final_list.append(pf)
    return final_list


def create_dataframe_from_list(final_list):
    df1 = pd.DataFrame(final_list, columns=['GTRLabMethod_ID', 'GTRLabTest_ID', 'MethodCategory', 'TestMethod', 'SpecimenType',
                                            'TestComment'])
    df2 = df1.set_index(['GTRLabMethod_ID', 'GTRLabTest_ID']).apply(lambda x: x.apply(pd.Series).stack()).reset_index().drop(['level_2'],1)
    df2.fillna(method = 'ffill', inplace = True)

    return df2

def output_file(df2):
    df2.to_csv(r'C:\Users\nkhatri\OneDrive - American Medical Association\Desktop\gtr_ftp.xml\GTR_LabTestMethod_v2.csv', index=False, na_rep='None')


main()