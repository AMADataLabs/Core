#!C:/Users/vigrose/AppData/Local/Continuum/anaconda3\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'astropy==3.2.1','console_scripts','showtable'
__requires__ = 'astropy==3.2.1'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('astropy==3.2.1', 'console_scripts', 'showtable')()
    )
