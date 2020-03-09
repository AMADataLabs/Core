#!/usr/bin/env python

from   abc import ABC, abstractmethod
import gc

import pandas as pd

import settings


class EntityTableCleaner():
    def __init__(self, input_path, output_path):
        self._input_path = input_path
        self._output_path = output_path

    def clean(self):
        table = pd.read_csv(intput_path, dtype=str)

        self._clean_table(table)

        

gc.collect()

print('Reading')
entity_comm_at = pd.read_csv('entity_comm_at.csv', dtype=str)

print('Trimming')
# trim to only get addr
entity_comm_at['comm_cat'] = entity_comm_at['comm_cat'].apply(str.strip)
entity_comm_at = entity_comm_at[entity_comm_at['comm_cat']=='A']

print('Stripping')
# strip all cols
for col in entity_comm_at.columns.values:
    entity_comm_at[col] = entity_comm_at[col].apply(str.strip)

print('Saving')
entity_comm_at.to_csv('str_entity_comm_at.csv', index=False)
del entity_comm_at
gc.collect()

del entity_comm_at
gc.collect()


# In[6]:


print('Reading')
entity_comm_usg_at = pd.read_csv('entity_comm_usg_at.csv', dtype=str)

print('Trimming')
entity_comm_usg_at['comm_cat'] = entity_comm_usg_at['comm_cat'].apply(str.strip)
entity_comm_usg_at = entity_comm_usg_at[entity_comm_usg_at['comm_cat'] == 'A']

print('Stripping')
for col in entity_comm_usg_at.columns.values:
    entity_comm_usg_at[col] = entity_comm_usg_at[col].apply(str.strip)
    
print('Saving')
entity_comm_usg_at.to_csv('str_entity_comm_usg_at.csv', index=False)

print('Releasing')
del entity_comm_usg_at
gc.collect()


# In[7]:


print('Reading')
entity_key_et = pd.read_csv('entity_key_et.csv', dtype=str)

print('Stripping')
for col in entity_key_et.columns.values:
    entity_key_et[col] = entity_key_et[col].apply(str.strip)

print('Saving')
entity_key_et.to_csv('str_entity_key_et.csv', index=False)

print('Releasing')
del entity_key_et
gc.collect()


# In[8]:


print('Reading')
license_lt = pd.read_csv('license_lt.csv', dtype=str)

print('Stripping')
for col in license_lt.columns.values:
    license_lt[col] = license_lt[col].apply(str.strip)
    
print('Saving')
license_lt.to_csv('str_license_lt.csv', index=False)

print('Releasing')
del license_lt
gc.collect()


# In[9]:


print('Reading')
post_addr_at = pd.read_csv('post_addr_at.csv', dtype=str)

print('Stripping')
for col in post_addr_at.columns.values:
    post_addr_at[col] = post_addr_at[col].apply(str.strip)
    
print('Saving')
post_addr_at.to_csv('str_post_addr_at.csv', index=False)

print('Releasing')
del post_addr_at
gc.collect()


# In[ ]:




