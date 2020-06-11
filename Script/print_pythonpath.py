import os

import repo


if __name__ == '__main__':
    repo.configure()

    print(os.environ.get('PYTHONPATH'))