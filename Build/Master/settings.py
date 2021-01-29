
import os
import sys

import dotenv

dotenv_path = os.environ.get('DOTENV_PATH')
if dotenv_path:
    dotenv.load_dotenv(dotenv_path=dotenv_path)
else:
    dotenv.load_dotenv()

for p in os.environ.get('DATALABS_PYTHONPATH', '').split(os.pathsep)[::-1]:
    sys.path.insert(0, p)
