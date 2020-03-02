
# ConnectPyODBC
# 	This snippet shows an example of how to connect to a database in Python and how to query it.


# Requirements:
#	Database authentication
#	text file in same directory as script with 2 lines of text. 
#		1st line: username 
#		2nd line: password



import pandas as pd
import pyodbc

with open('auth.txt', 'r') as file:
    
    # Make connection to AIMS
    s = "DSN=aims_prod; UID={}; PWD={}".format(file.readline().replace('\n',''), file.readline().replace('\n',''))
    aimsprod = pyodbc.connect(s)
    file.close()

# read input CSV file
df = pd.read_csv(filename, dtype=object)