""" Generic database object intended to be subclassed by specific databases. """
from   abc import abstractmethod
from   dataclasses import dataclass
import os

import pandas
import sqlalchemy

import datalabs.access.database as db


class Database(db.Database):
    @property
    def engine(self):
        return self._connection

    def connect(self):
        self._connection = sqlalchemy.create_engine(self.url, echo=True)
