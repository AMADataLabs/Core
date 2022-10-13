from   dataclasses import dataclass
import logging
import os
import subprocess

from   pathlib import Path

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

@dataclass
class FileDetails:
    commit: str
    size: int
    name: Path


TEN_MB = 10 * 1024 * 1024


def main():
    file_details = get_file_details()

    large_file_details = extract_large_files(file_details)

    print_files(large_file_details)


def get_file_details():
    raw_file_details = get_raw_file_details()

    return parse_file_details(raw_file_details)


def extract_large_files(file_details):
    large_files = []

    for file_detail in file_details:
        if file_detail.size >= TEN_MB:
            file_detail.size = int(file_detail.size / 1024 / 1024)
            large_files.append(file_detail)

    return large_files

def print_files(file_details):
    for file_detail in file_details:
        prefix = ""
        size = 0

        if file_detail.name.is_file():
            prefix = "*"

            if os.stat(file_detail.name).st_size >= TEN_MB:
                prefix += "§"

        print(f"{prefix}{file_detail.commit} {file_detail.size}MiB {file_detail.name}")


def get_raw_file_details():
    process = subprocess.run(["git", "rev-list", "--objects", "--all"], stdout=subprocess.PIPE)
    process = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objecttype) %(objectname) %(objectsize) %(rest)"],
        input=process.stdout,
        stdout=subprocess.PIPE
    )
    process = subprocess.run(["sed", "-n", "s/^blob //p"], input=process.stdout, stdout=subprocess.PIPE)
    process = subprocess.run(["sort", "--numeric-sort", "--key=2"], input=process.stdout, stdout=subprocess.PIPE)
    process = subprocess.run(["cut", "-c", "1-12,41-"], input=process.stdout, stdout=subprocess.PIPE)

    return process.stdout.decode().split("\n")[:-1]


def parse_file_details(raw_file_details):
    file_details = []

    for line in raw_file_details:
        commit = line[:12]

        size, name = line[12:].strip().split(" ", 1)

        file_details.append(FileDetails(commit, int(size), Path(name)))

    return file_details

if __name__ == "__main__":
    main()
