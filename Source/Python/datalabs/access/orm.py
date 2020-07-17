""" Generic database object intended to be subclassed by specific databases. """
import sqlalchemy
from   sqlalchemy.orm import sessionmaker

from   datalabs.access.credentials import Credentials
import datalabs.access.database as db
from   datalabs.task import Task




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
class DatabaseTaskMixin(Task):
    def _get_database(self):
        config = db.Configuration(
            name=self._parameters.database['name'],
            backend=self._parameters.database['backend'],
            host=self._parameters.database['host']
        )
        credentials = Credentials(
            username=self._parameters.database['username'],
            password=self._parameters.database['password']
        )

        return Database(config, credentials)
