from datetime import datetime, timedelta
import logging
import sqlite3

log_file = r"egl_booking_handler\logs\events.log"

logger = logging.getLogger('events.log')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(message)s')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

log_format = str()

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):

    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


def create_booking(conn, booking):

    sql = "INSERT INTO bookings(" + ', '.join(
        f"{key}" for key in booking.keys()) + ") VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?)"
    
    cur = conn.cursor()
    cur.execute(sql, list(booking.values()))
    conn.commit()


def execute_sqlite(conn, booking, same_date, cancellation):
    
    cur = conn.cursor()
    
    # Check revised number if booking number exists in table
    cur.execute("SELECT revised_no from bookings WHERE booking_no = ?", (booking['booking_no'],))
    booking_exists = cur.fetchone()

    # If booking does not exist and needs to be created then set revised number to 0
    if booking_exists:
        revised_no = booking_exists[0]
    else:
        revised_no = 0

    # Check if pdf name is already in table
    cur.execute("SELECT pdf_name from bookings WHERE instr(pdf_name, ?) > 0", (booking['pdf_name'],))
    pdf_exists = cur.fetchone()

    # Get booking number if it exists in table
    cur.execute("SELECT booking_no from bookings WHERE booking_no = ?", (booking['booking_no'],))
    booking_no = cur.fetchone()

    dict_with_updates = {}

    # This value is used in main.py to determine if the booking should be created, updated or deleted
    string = str()

    # same_date is received from pdf_parser.py and is True if the pdf file is sent on the same date as the ATD
    if same_date:
        # Same date as ATD
        log_format = f"{booking['booking_no']} not updated, file sent same date as ATD."

        # No update in Navis, moves e-mail to no change folder
        string = "SAME DATE"

    # If pdf name exists in table and booking number exists in table then do nothing
    elif pdf_exists:
        log_format = f"Pdf {booking['pdf_name']} already exists in table."

        # No update in Navis, moves e-mail to no change folder
        string = "PDF EXISTS"
    
    # cancellation is received from pdf_parser.py and is True if the pdf file is a cancellation
    elif cancellation:
        # If booking exists in table then delete it, else do nothing (should not happen)
        if booking_exists:
            delete_booking(conn, booking_no)

            # Deletes booking in Navis, moves e-mail to cancelled folder
            string = "DELETE BOOKING"
            log_format = f"Cancellation. {booking['booking_no']} is removed from table."
        else:
            # Does nothing but moves e-mail to cancelled folder
            string = "SHOULD DELETE BUT BOOKING DOES NOT EXIST"
            log_format = f"Booking {booking['booking_no']} does not exist in database. Cannot cancel a booking that does not exist."
        
    # If booking does not exist then create it in database
    elif booking_exists is None:
        create_booking(conn, booking)

        # Create booking in Navis, moves e-mail to database folder
        string = "CREATE BOOKING"
        log_format = f"{booking['booking_no']} is added to table."
    
    # If revised_no is higher than the received booking then do nothing (should not happen)
    elif revised_no > int(booking['revised_no']):
        log_format = f"Revised no is less than already existing no for {booking['booking_no']} in table."

        # No update in Navis, moves e-mail to no change folder
        string = "REVISED NO. LESS THAN EXISTING"
    
    # If revised_no is lower than the received booking then update the booking in database
    elif revised_no < int(booking['revised_no']):
        dict_with_updates = update_booking(conn, booking, 'booking_no', booking['booking_no'])

        # Update booking in Navis, moves e-mail to database folder
        string = "UPDATE BOOKING"
        log_format = f"{booking['booking_no']} is updated. Revision no: {booking['revised_no']}."

    elif revised_no == int(booking['revised_no']):
        log_format = f"Revised no is equal to already existing no for {booking['booking_no']} in table."

        # No update in Navis, moves e-mail to no change folder
        string = "REVISED EQUAL TO EXISTING"
        
    
    logger.info(log_format)
    return string, booking_no, dict_with_updates


def update_booking(conn, parsed_info, key_name, key_value):
    cur = conn.cursor()

    cur.execute("SELECT * from bookings WHERE booking_no = ?", (parsed_info['booking_no'],))
    db_row = cur.fetchone()

    bool_dict = {}
    for db_value, parsed_key in zip(db_row, parsed_info.keys()):
        if db_value == parsed_info.get(parsed_key):
            bool_dict[parsed_key] = False
        else: bool_dict[parsed_key] = True

    parsed_info['pdf_name'] = f"{db_row[20]}, {parsed_info.get('pdf_name')}"

    sql = "UPDATE bookings SET " + ', '.join(
        f"{key}=?" for key in parsed_info.keys()) + f" WHERE {key_name}=?"
    
    cur.execute(sql, list(parsed_info.values()) + [key_value])
    conn.commit()
    return bool_dict


def get_booking_data(conn, booking):
    cur = conn.cursor()
    
    # Check revised number if booking number exists in table
    cur.execute("SELECT * from bookings WHERE booking_no = ?", (booking['booking_no'],))
    db_row = cur.fetchone()

    # Create dictionary with booking data
    bookings_dict = {}
    for db_value, parsed_key in zip(db_row, booking.keys()):
        bookings_dict[parsed_key] = db_value
    
    return bookings_dict


def delete_booking(conn, booking):
    sql = "DELETE FROM bookings where booking_no = ?"

    cur = conn.cursor()
    cur.execute(sql, booking)
    conn.commit()


def delete_all_bookings(conn):
    sql = 'DELETE FROM bookings'
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except sqlite3.Error as e:
        print(e)


def main():

    database = "sqlite\sqlite_egl.db"

    sql_create_booking_table = """CREATE TABLE IF NOT EXISTS bookings (
                                    cancellation text,
                                    revised_no int,
                                    booking_no text PRIMARY KEY,
                                    date_booked text,
                                    etd text,
                                    navis_voy text,
                                    pod text,
                                    tod text,
                                    ocean_vessel text,
                                    voyage text,
                                    final_dest text,
                                    commodity text,
                                    count_40hc int,
                                    count_40dv int,
                                    count_20dv int,
                                    weight_40hc int,
                                    weight_40dv int,
                                    weight_20dv int,
                                    hazard_40hc text,
                                    hazard_40dv text,
                                    hazard_20dv text,
                                    pdf_name text
                                );"""
    
    conn = create_connection(database)

    if conn is not None:
        create_table(conn, sql_create_booking_table)
    else:
        print("Error! Cannot create database connection.")

def add_columns_to_table(conn, table_name, column_names, column_types):
    cur = conn.cursor()

    if isinstance(column_names, list):
        sql = f"ALTER TABLE {table_name} ADD ("

        for name, type in zip(column_names, column_types):
            sql += f"{name} {type}, "
        
        sql = sql[:-2] + ");"
    else:
        sql = f"ALTER TABLE {table_name} ADD {column_names} {column_types};"

    cur.execute(sql)
    conn.commit()

def update_values_in_column(conn, table_name, column_name, column_value, where_column=None, where_value=None):
    cur = conn.cursor()

    sql = f"UPDATE {table_name} SET {column_name} = {column_value}"

    if where_value is not None:
        sql += f" WHERE {where_column}={where_value}"

    cur.execute(sql)
    conn.commit()


def get_bookings_where_values_not_in_db(conn, navis=None, terminal=None):
    cur = conn.cursor()

    if navis is not None:
        sql = f"SELECT booking_no, navis_voy FROM bookings WHERE booking_in_navis=False"

    elif terminal is not None:
        date_today = datetime.today().strftime('%Y/%m/%d')
        one_year_from_today = (datetime.today() + timedelta(days=365)).strftime('%Y/%m/%d')
        sql = f"SELECT booking_no FROM bookings WHERE (tod = '' OR tod IS NULL) AND (etd BETWEEN '{date_today}' AND '{one_year_from_today}')"
        
    else:
        return None
    
    cur.execute(sql)
    rows = cur.fetchall()

    return rows


def drop_column_from_table(conn, table_name, column_name) -> None:

    cur = conn.cursor()
    sql = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    cur.execute(sql)
    conn.commit()



if __name__ == '__main__':
    pass

    #conn = create_connection("egl_booking_handler\sqlite\sqlite_egl.db")
    #update_values_in_column(conn, "bookings", "booking_in_navis", 0, "booking_no", "503300008420")
    #update_values_in_column(conn, "bookings", "booking_in_navis", 1)
    #print(get_bookings_where_values_not_in_db(conn))
    #drop_column_from_table(conn, "bookings", "booking_in_navis")'
    #add_columns_to_table(conn, "bookings", "booking_in_navis", "integer")