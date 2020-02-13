from pathlib import Path
from platform import system
import sys


run = Path('python Script/run.py')


def task_test():

    actions = [
        # f'{export} PYTHONPATH={str(path)} python -m pytest',
        f'{run} python -m pytest',
    ]

    return dict(
        actions=actions,
        verbosity=2,
    )
