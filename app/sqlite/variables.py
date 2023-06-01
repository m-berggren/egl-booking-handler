import configparser
from pathlib import Path


def database_file() -> str:
    """Return the database file name."""
    config = configparser.ConfigParser()
    config.read(ROOT_DIR / 'sqlite_database.ini')
    file = config['database']['database_file']
    return file

ROOT_DIR = Path(__file__).parents[2]
SHAREPOINT_DIR = Path(__file__).parents[5]
DATABASE_FILE = database_file()
ERROR_LOG_FILE = ROOT_DIR / 'logs/sqlite_error.log'


