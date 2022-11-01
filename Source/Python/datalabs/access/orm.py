""" Generic database object intended to be subclassed by specific databases. """
import logging

import pandas
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

import datalabs.access.database as db

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class Database(db.Database):
    def connect(self):
        LOGGER.info("Database connection URL: %s", self.url)
        engine = sqlalchemy.create_engine(self.url, echo=True)
        Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name

        self._connection = Session()

    def read(self, sql: str, **kwargs):
        return pandas.read_sql(sql, self._connection.connection(), **kwargs)

    def add(self, model, **kwargs):
        self._connection.add(model, **kwargs)

    def delete(self, model, **kwargs):
        self._connection.delete(model, **kwargs)

    def update(self, model, **kwargs):
        self._connection.update(model, **kwargs)

    def commit(self):
        self._connection.commit()

    def query(self, *models, **kwargs):
        return self._connection.query(*models, **kwargs)

    def execute(self, sql, **kwargs):
        return self._connection.execute(sql, **kwargs)
