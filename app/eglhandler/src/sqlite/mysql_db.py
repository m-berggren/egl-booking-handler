from sqlalchemy import create_engine, MetaData, Table
import yaml

from eglhandler.src.sqlite.declare_models import Base


class MySQL:
    """MySQL database class"""

    def __init__(self, config:dict) -> None:
        settings = config['mysql']

        self.user = settings['user']
        self.pw = settings['password']
        self.host = settings['host']
        self.db = settings['db_name']
        

    def create_connection(self) -> Table:
        """ Connect to MySQL database"""

        engine = create_engine(f"mysql+mysqlconnector://{self.user}:{self.pw}@{self.host}/{self.db}", echo=True)
        engine.connect()

        return engine

    def create_table(self) -> None:
        """ Create table in MySQL database"""

        engine = create_engine(f"mysql+mysqlconnector://{self.user}:{self.pw}@{self.host}/{self.db}", echo=True)
        engine.connect()
        Base.metadata.create_all(engine)
        metadata = MetaData()

        return Table('bookings', metadata, autoload_with=engine)

