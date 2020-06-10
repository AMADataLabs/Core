""" Generic database object intended to be subclassed by specific databases. """
from   abc import abstractmethod
from   dataclasses import dataclass
import os

import pandas
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

import datalabs.access.database as db


class Database(db.Database):
    @property
    def session(self):
        Session = sessionmaker(bind=self._connection)

        return Session()

    def connect(self):
        self._connection = sqlalchemy.create_engine(self.url, echo=False)

    def close(self):
        pass
