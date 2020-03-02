import logging
import logging.handlers
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def set_log_file(filename, format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    filehandler = logging.FileHandler(filename=filename)
    filehandler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(format_string)
    filehandler.setFormatter(file_formatter)
    root.addHandler(filehandler)


if __name__ == '__main__':
    logging.info("HELLO")
