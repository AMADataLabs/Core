# Script for taking in a csv and outputing a Benerator xml config chunk for geenrating synthetic data based on it

import pandas as pd
import numpy as np

filepath = input("filepath to .csv: ")
df = pd.read_csv(filepath, dtype=str)
i = 0
output = []

def is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

for c in df.columns:

    # processing
    try:
        df[c] = df[c].str.strip()
        df[c] = df[c].replace(to_replace=np.nan, value="0")
        df[c] = df[c].replace(to_replace='', value="0")
        df[c] = pd.to_numeric(df[c])
    except ValueError:
        df[c] = df[c].str.strip()
        df[c] = df[c].astype(str)

    # generating xml lines
    upper = df[c].max()
    lower = df[c].min()

    if i == 0:
        # Primary Key
        output += [f'<id name="{c}" type="string" pattern="[0-9]{{{len(str(upper))}}}"/>']
    else:
        distinct = df[c].unique()

        # Categorical field
        if len(distinct) < 100:
            value_str = ""
            for s in distinct:
                value_str += "'" + str(s) + "',"
            output += [f'<attribute name="{c}" values="{value_str[:-1]}"/>']

        # Random String field, length matches .max() len
        elif type(upper) is str:
            output += [f'<attribute name="{c}" type="string" pattern="[A-Z]{{{len(upper)}}}"/>']

        # Random Int field, length matches .max() len
        elif type(upper) is int:
            output += [f'<attribute name="{c}" distribution="random" type="int" min="{lower}" max="{upper}" />']

        # Random Float field, length matches .max() len
        elif type(upper) is float:
            output += [f'<attribute name="{c}" distribution="random" type="float" min="{lower}" max="{upper}" />']

    i += 1

for out in output:
    print(out)



