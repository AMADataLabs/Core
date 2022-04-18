import os
import sys

from   datalabs.plugin import import_plugin
import settings


def main():
    task_wrapper_class = import_plugin(os.environ['TASK_WRAPPER_CLASS'])
    task_wrapper = task_wrapper_class(parameters=sys.argv)

    return task_wrapper.run()


if __name__ == '__main__':
    main()
