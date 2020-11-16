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
            name=parameters.get('name') or parameters.get('NAME'),
            backend=parameters.get('backend') or parameters.get('BACKEND'),
            host=parameters.get('host') or parameters.get('HOST'),
            port=parameters.get('port') or parameters.get('PORT')
        )
        credentials = Credentials(
            username=parameters.get('username') or parameters.get('USERNAME'),
            password=parameters.get('password') or parameters.get('PASSWORD')
        )

        return Database(config, credentials)
