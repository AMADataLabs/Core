
import os
import sys

import dotenv

dotenv.load_dotenv()

for p in os.environ.get('DATALABS_PYTHONPATH', '').split(os.pathsep)[::-1]:
    sys.path.insert(0, p)
