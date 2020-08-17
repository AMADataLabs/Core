""" Generic database object intended to be subclassed by specific databases. """
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.credentials import Credentials
import datalabs.access.database as db




class Database(db.Database):
    @property
    def session(self):
        Session = sessionmaker(bind=self._connection)  # pylint: disable=invalid-name

        return Session()

    def connect(self):
        self._connection = sqlalchemy.create_engine(self.url, echo=False)

    def close(self):
        pass


# pylint: disable=abstract-method
class DatabaseTaskMixin:
    @classmethod
    def _get_database(cls, parameters):
        config = db.Configuration(
            name=parameters['name'],
            backend=parameters['backend'],
            host=parameters['host']
        )
        credentials = Credentials(
            username=parameters['username'],
            password=parameters['password']
        )

        return Database(config, credentials)
