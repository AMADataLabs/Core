""" Generic database object intended to be subclassed by specific databases. """
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

import datalabs.access.database as db


class Database(db.Database):
    def connect(self):
        engine = sqlalchemy.create_engine(self.url, echo=True)
        Session = sessionmaker(bind=engine)  # pylint: disable=invalid-name

        self._connection = Session()

    def add(self, model, **kwargs):
        self._connection.add(model, **kwargs)

    def commit(self):
        self._connection.commit()

    def query(self, *models, **kwargs):
        return self._connection.query(*models, **kwargs)
