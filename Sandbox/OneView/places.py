import pandas as pd


def merge_meri(inst_name, inst_address):
    '''Add meri addresses'''
    inst = pd.merge(inst_name, inst_address, on='ins_id')
    inst = inst.drop_duplicates(['ins_id','ins_pers_add1'])
    return inst

def merge_meri_cred(meri, cred):
    '''Find MERI/credentialing overlap'''
    matches = pd.merge(cred, meri, left_on=['Street 1ST','City', 'State'], right_on=['ins_pers_add1', 'ins_pers_city', 'ins_pers_state'])
    matches = matches[['Customer Number','ins_id']]
    return matches

def merge_iqvia_cred(iqvia, cred):
    '''Find credentialing/IQVia overlap'''
    cred = cred.fillna('None')
    cred['Street 1ST']=[x.upper() for x in cred['Street 1ST']]
    cred['City']=[x.upper() for x in cred['City']]
    cred['State']=[x.upper() for x in cred['State']]
    matches = pd.merge(cred, iqvia, left_on=['Street 1ST','City', 'State'], right_on=['PHYSICAL_ADDR_1', 'PHYSICAL_CITY', 'PHYSICAL_STATE'])
    matches = matches[['Customer Number','ims_org_id']]
    return matches

def merge_meri_iqvia(meri, iqvia):
    '''Find MERI/IQVia overlap'''
    meri = meri.fillna('None')
    meri['ins_pers_add1']=[x.upper() for x in meri['ins_pers_add1']]
    meri['ins_pers_city']=[x.upper() for x in meri['ins_pers_city']]
    matches = pd.merge(meri, iqvia, left_on=['ins_pers_add1', 'ins_pers_city', 'ins_pers_state'], right_on=['PHYSICAL_ADDR_1', 'PHYSICAL_CITY', 'PHYSICAL_STATE'])
    matches = matches[['ins_id','ims_org_id']]
    return matches

def merge_all(meri_cred, iqvia_cred, meri_iqvia):
    on_cred = pd.merge(meri_cred, iqvia_cred, on = 'Customer Number', how='outer')
    places = pd.merge(on_cred, meri_iqvia, on = 'ims_org_id', how='outer')
    places = places.drop_duplicates()
    return places

def places():
    '''Create key table'''
    credential = pd.read_excel('../../Data/Credentialling/Org_Addresses.xlsx')
    inst_name = pd.read_excel('../../Data/MasterfileCore/Institution.xlsx')
    inst_address = pd.read_excel('../../Data/MasterfileCore/Institution_Personnel.xlsx')
    iqvia = pd.read_csv('../../Data/MasterfileCore/Aah.csv')
    meri = merge_meri(inst_name, inst_address)
    meri_cred = merge_meri_cred(meri, credential)
    iqvia_cred = merge_iqvia_cred(iqvia, credential)
    meri_iqvia = merge_meri_iqvia(meri, iqvia)
    places = merge_all(meri_cred, iqvia_cred, meri_iqvia)
    places.to_csv('../../Data/MasterfileCore/Places.csv', index=False)


if __name__ == "__main__":
    places()

