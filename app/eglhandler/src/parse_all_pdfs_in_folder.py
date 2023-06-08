import logging
import os
import shutil

import pandas as pd
from tqdm import tqdm

from eglhandler.src.parser.pdf_parser import booking_info
from eglhandler.src.sqlite.sqlite_db import SqliteDB

DATABASE = r"C:\Users\SWV224\Documents\egl-booking-handler\app\eglhandler\logs\egl_sqlite.db"

def main():
    DOWNLOAD_DIR = r"C:\Users\SWV224\Desktop\pdfs\downloaded"
    PARSED_DIR = r"C:\Users\SWV224\Desktop\pdfs\parsed"
    REVISED_NO_FILE = r"C:\Users\SWV224\Documents\egl-booking-handler\app\eglhandler\logs\same_revised_no.txt"
    DATAFRAME_FILE = r"C:\Users\SWV224\Documents\egl-booking-handler\app\eglhandler\logs\parser_df.csv"
    LOG_FILE = r"C:\Users\SWV224\Documents\egl-booking-handler\app\eglhandler\logs\sqlite_error.log"

    logger = logging.getLogger('sqlite_error.log')
    logger.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s | %(message)s')
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    def parse_all_pdfs_in_folder():

        sql_table = SqliteDB(DATABASE)
        cur = sql_table.conn.cursor()

        df = pd.DataFrame()

        # LOOP THROUGH ALL PDFS IN FOLDER
        for pdf_file in tqdm(os.listdir(DOWNLOAD_DIR)):
            if not pdf_file.endswith(".PDF"):
                continue

            # PARSE PDF
            booking, same_date, cancellation, terminal = booking_info(DOWNLOAD_DIR, pdf_file)
            
            if booking is None:
                continue

            # Check revised number if booking number exists in table
            cur.execute("SELECT revised_no from egl_bookings WHERE booking_no = ?", (booking['booking_no'],))
            booking_exists = cur.fetchone()

            # If booking does not exist and needs to be created then set revised number to 0
            if booking_exists:
                revised_no = booking_exists[0]
            else:
                revised_no = 0

            # Create dataframe and append dict to it
            if df.empty:
                df = pd.DataFrame(booking, index=[0])
            else:
                df = pd.concat([df, pd.DataFrame(booking, index=[0])], ignore_index=True)
                
            # Check if pdf name is already in table
            cur.execute("SELECT pdf_name from egl_bookings WHERE instr(pdf_name, ?) > 0", (booking['pdf_name'],))
            pdf_exists = cur.fetchone()

            # Get booking number if it exists in table
            cur.execute("SELECT booking_no from egl_bookings WHERE booking_no = ?", (booking['booking_no'],))
            booking_no = cur.fetchone()

            cur.execute("SELECT cancellation from egl_bookings WHERE booking_no = ?", (booking['booking_no'],))
            cancellation_exists_in_db = cur.fetchone()

            # If statments below
            if pdf_exists:
                #print('pdf exists')
                pass
            elif booking_exists is None:
                sql_table.create_booking(booking)
                #print('booking exists')
            elif cancellation:
                #print('cancellation')
                sql_table.update_booking_with_cancellation(booking)
            elif revised_no > int(booking['revised_no']):
                #print('revised more than existing')
                sql_table.update_booking_even_if_lower_revised_no(booking)
            elif revised_no < int(booking['revised_no']):
                #print('revised no less than existing')
                sql_table.update_booking(booking)
            elif cancellation_exists_in_db:
                #print('cancellation exists')
                sql_table.when_cancellation_exists_in_db(booking)
            elif revised_no == int(booking['revised_no']):
                #print('revised no same as existing')
                with open(REVISED_NO_FILE, 'a') as f:
                    f.write(f'{booking["booking_no"]} revised no {booking["revised_no"]} already exist. Pdf: {pdf_exists}\n')

            shutil.move(os.path.join(DOWNLOAD_DIR, pdf_file), os.path.join(PARSED_DIR, pdf_file))

        df.to_csv(DATAFRAME_FILE)

    parse_all_pdfs_in_folder()


def set_up_db():

    table_dict = {
        'cancellation': 'TEXT',
        'revised_no': 'INT',
        'booking_no': 'TEXT PRIMARY KEY',
        'booking_in_navis': 'TEXT',
        'date_booked': 'TEXT',
        'etd': 'TEXT',
        'navis_voy': 'TEXT',
        'pod': 'TEXT',
        'tod': 'TEXT',
        'ocean_vessel': 'TEXT',
        'voyage': 'TEXT',
        'final_dest': 'TEXT',
        'commodity': 'TEXT',
        'count_40hc': 'INT',
        'count_40dv': 'INT',
        'count_20dv': 'INT',
        'weight_40hc': 'INT',
        'weight_40dv': 'INT',
        'weight_20dv': 'INT',
        'hazard_40hc': 'TEXT',
        'hazard_40dv': 'TEXT',
        'hazard_20dv': 'TEXT',
        'pdf_name': 'TEXT',
    }

    # Create database
    sql_table = SqliteDB(DATABASE, table_name='egl_bookings')
    sql_table.create_table(table_dict)

#set_up_db()
main()