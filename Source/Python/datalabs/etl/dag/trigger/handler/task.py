from   abc import ABCMeta, ABC, abstractmethod

from  datalabs.task import Task

class TriggerHandler(Task, ABC):
    def run(self):
        pass

    @abstractmethod
    def
