import os
import sys

from   datalabs.plugin import import_plugin
import settings


def main():
    task_class = import_plugin(os.environ['TASK_CLASS'])
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task = task_wrapper_class(task_class, parameters=sys.argv)

    return task.run()


if __name__ == '__main__':
    main()
