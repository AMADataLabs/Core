import os

import repo

repo.configure()

print(os.environ.get('PYTHONPATH'))
