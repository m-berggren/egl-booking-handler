import pandas as pd
import yaml

from eglhandler.src.sqlite.mysql_db import MySQL


def run_class():
    with open('app\eglhandler\config.yaml', 'r') as _f:
        config = yaml.safe_load(_f)

    data = MySQL(config)
    table = data.create_table()
    print(table.columns.keys())

def create_table():
    with open('app\eglhandler\config.yaml', 'r') as _f:
        config = yaml.safe_load(_f)

    df = pd.read_csv(r"C:\Users\SWV224\Desktop\egl_bookings_23-07-08.csv")
    df.to_sql('bookings', MySQL(config).create_connection(), if_exists='append', index=False)

run_class()
#create_table()