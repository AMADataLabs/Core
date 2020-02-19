from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, PrimaryKeyConstraint, Column, String, Integer, Date, JSON, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from configparser import ConfigParser
import pandas as pd

Base = declarative_base()

class PhoneInfoCSV(Base):
    __tablename__ = 'csv_results_test'

    event_id = Column(Integer, primary_key=True)
    phone_number = Column(String)
    city = Column(String, nullable=True)
    time_of_insert = Column(TIMESTAMP, server_default=func.now())
    date = Column(String, nullable=True)
    name = Column(String, nullable=True)
    notes = Column(ARRAY(String), nullable=True)
    phone_type = Column(String, nullable=True)
    provider = Column(String, nullable=True)
    quality_score = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)
    wslive_status = Column(String, nullable=True)
    response = Column(JSON, nullable=True)





class PostgresInterface:

    def __init__(self, database, filename='database.ini', section='postgresql'):
        configuration = self.config(filename=filename, section=section)
        self.host = configuration['host']
        self.user = configuration['user']
        self.database = database
        self.section = section
        password = configuration['password']
        connection_string = section + "://%s:%s@%s/%s" % (self.user, password, self.host, self.database)
        connecting_string = "Connecting to %s database: %s with username %s" % (self.section, self.database, self.user)
        print(connecting_string)
        self.engine = create_engine(connection_string)
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()

    def disconnect(self):
        if self.session is not None:
            disconnect_string = "Disconnecting from %s database: %s with username %s" % (self.section, self.database, self.user)
            print(disconnect_string)
            self.engine.dispose()

    def create_all_tables(self):
        metadata = MetaData(self.engine)
        metadata.create_all()

    def add_result(self, result):
        return self.session.add(result)
    
    def commit():
        return self.session.commit()

    def insert_into_table(self, events, table):
        events_to_add = []
        for event in events:
            to_pass = {}
            to_pass['city'] = event['city']
            to_pass['date'] = event['date']
            to_pass['name'] = event['name']
            if event['notes'] is not None:
                to_pass['notes'] = event['notes'].split(',')
            to_pass['phone_type'] = event['phone_type']
            to_pass['provider'] = event['provider']
            to_pass['quality_score'] =  event['quality_score']
            to_pass['state'] = event['state']
            to_pass['zipcode'] = event['zipcode']
            to_pass['wslive_status'] = event['wslive_status']
            to_pass['response'] = event['response']
            print(event['response'])
            to_pass['phone_number'] = event['phone_number']
            events_to_add.append(table(**to_pass))
        for event in events_to_add:
            self.add_result(event)
        self.session.commit()
    

    def config(self, filename, section):
        # Creates a parser
        parser = ConfigParser()
        # Read the configuration file for host, database, user, and password
        parser.read(filename)

        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception("Section {0} not found in the {1} file".format(section, filename))

        return db



"""

Getting the latest connected numbers

SELECT DISTINCT ON (phone_number)
* 
FROM test_rpv_results5
ORDER BY phone_number, date DESC;

"""
    

if __name__ == '__main__':
    try:
        db_interface = PostgresInterface('phone_info')
        df = pd.read_csv('result.txt')
        df = df.where((pd.notnull(df)), None)
        df = df.replace('None', None)
        df = df.replace('None.*', None, regex=True)
        df = df.replace('', None)
        events = []
        for key, item in df.iterrows():
            to_pass = {}
            to_pass['city'] = item.City 
            to_pass['date'] = item.Date 
            to_pass['name'] = item.Name
            to_pass['notes'] = item.Notes
            to_pass['phone_type'] = item.PhoneType
            to_pass['provider'] = item.Provider
            to_pass['quality_score'] =  item.QualityScore
            to_pass['state'] = item.State
            to_pass['zipcode'] = item.Zipcode
            to_pass['wslive_status'] = item.WSLive_Status
            to_pass['response'] = item.response
            to_pass['phone_number'] = item.OFFICE_TELEPHONE
            events.append(to_pass)
        db_interface.insert_into_table(events, PhoneInfoCSV)
    finally:
        if db_interface is not None:
            db_interface.disconnect()


