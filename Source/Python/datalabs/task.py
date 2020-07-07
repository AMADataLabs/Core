""" Abstract task base class for use with AWS Lambda and other task-based systems. """
from abc import ABC, abstractmethod


class Task:
    @abstractmethod
    def run(self):
        pass
