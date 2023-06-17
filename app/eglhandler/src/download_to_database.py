import os
import shutil

import yaml

from eglhandler.src.graph.graph import Graph, EGL
from eglhandler.src.parser import pdf_parser
from eglhandler.src.sqlite.sqlite_db import SqliteDB

def only_download_emails_and_update_database():
    """ This program will only download emails from folder and update the database.
    
    It will:
    1. Download emails from Outlook
    2. Parse pdfs
    3. Import to database
    6. Move pdfs to parsed folder
    7. Move emails to processed folder

    All bookings handled are saved in a database but also a csv file.
    """

    with open(r'app\eglhandler\config.yaml', 'r') as _f:
        config = yaml.safe_load(_f)

    """ Set up graph- and egl objects."""
    graph: Graph = Graph(config)
    access_token = graph.generate_access_token(acquire_token_by="username_password")
    headers = graph.create_headers(access_token)
    egl: EGL = EGL(config, headers)

 
    # Constants
    DOWNLOAD_DIR = config['directories'].get('downloaded')
    PARSED_DIR = config['directories'].get('parsed')
    DATABASE = config['sqlite'].get('database')

    # Get email count
    email_count = egl.count_emails_in_folder()

    if email_count == 0:
        print("No email(s) found in folder.")
        return
    
    print(f"Processing {email_count} email(s)...\n")
    
    # Loop through emails, download pdf, parse pdf, import to database
    for count in range(email_count):
        
        # Downloads pdf from email and gets ID of email
        # The argument is used to find corresponding words in bodypreview
        email_id, terminal_found, pdf_file = egl.download_pdf_from_email(
            DOWNLOAD_DIR
            )

        # Parses pdf and gets booking info
        data, same_date, cancellation, terminal = pdf_parser.booking_info(
            DOWNLOAD_DIR,
            pdf_file,
            config
            )
        
        # If terminal was not found in pdf_parser, i.e. missing from pdf,
        # use terminal found in email bodypreview, if any
        if not data['tod']:
            data['tod'] = terminal_found
            terminal = terminal_found
            # Run functions to determine navis voyage again
        
        if data is None:
            print("data is none, skipping...")
            continue

        # This is where the booking is sent to the database
        sql_table = SqliteDB(DATABASE)
        cur = sql_table.conn.cursor()

        cur.execute(f"SELECT revised_no from egl_bookings WHERE booking_no = {data['booking_no']}")
        booking_exists = cur.fetchone()

        # If booking does not exist and needs to be created then set revised number to 0
        if booking_exists:
            revised_no = booking_exists[0]
        else:
            revised_no = 0

        # Check if pdf name is already in table
        cur.execute("SELECT pdf_name from egl_bookings WHERE INSTR(pdf_name, ?) > 0", (data['pdf_name'],))
        pdf_exists = cur.fetchone()

        cur.execute(f"SELECT booking_no from egl_bookings WHERE booking_no = {data['booking_no']}")
        booking_no = cur.fetchone()

        cur.execute("SELECT cancellation from egl_bookings WHERE booking_no = ? AND cancellation = 'CANCELLATION'", (data['booking_no'],))
        cancellation_exists_in_db = cur.fetchone()


        """ If statments below are used to determine what to do with the booking."""
        if not terminal:
            # If terminal is missing from pdf and bodypreview of e-mail
            print(f"{data['booking_no']} does not have a terminal.")
            egl.move_email_to_folder(email_id, 'no_terminal_folder_id')
            # Do more?

        elif same_date:
            # When booking is updated on the same day as ETD
            print(f"Update for {data['booking_no']} received same day as ETD.")
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif pdf_exists:
            # If name of pdf is already in database
            print(f"PDF-file for {data['booking_no']} already exists in database.")
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif cancellation:
            # If cancellation is found in pdf_parser
            if booking_exists:
                # When booking exists it can be removed
                print(f"Deleting {data['booking_no']} from database.")
                sql_table.update_booking_with_cancellation(data)
                egl.move_email_to_folder(email_id, 'cancel_folder_id')
            else:
                # If booking does not exist in database, but cancellation is found in pdf_parser
                print(f"{data['booking_no']} should be deleted but does not exist in database.")
                sql_table.update_booking_with_cancellation(data)
                egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif not booking_exists:
            # If booking does not exist in database create it
            print(f"Creating {data['booking_no']} in database.")
            sql_table.create_booking(data)
            egl.move_email_to_folder(email_id, 'db_folder_id')

        elif revised_no > int(data['revised_no']):
            # If revised number in pdf_parser is less than in database
            print(f"Revised number in {data['booking_no']} is less than in database.")
            sql_table.update_booking_even_if_lower_revised_no(data)
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif cancellation_exists_in_db:
            # If cancellation exists in database
            print(f"{data['booking_no']} already cancelled in database. Saving PDF file name.")
            sql_table.when_cancellation_exists_in_db()
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif revised_no < int(data['revised_no']):
            # If revised number in pdf_parser is greater than in database
            print(f"Updating {data['booking_no']} in database")
            boolean_dict = sql_table.update_booking(data)
            egl.move_email_to_folder(email_id, 'db_folder_id')
        
        elif revised_no == int(data['revised_no']):
            # If revised number in pdf_parser is equal to in database
            print(f"Revised number in {data['booking_no']} is equal to in database.")
            sql_table.update_booking(data)
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        # Moves pdf to new directory 
        shutil.move(
            os.path.join(DOWNLOAD_DIR, pdf_file),
            os.path.join(PARSED_DIR, pdf_file)
            )

        print(f"{count + 1} of {email_count} e-mail(s).", "\n")

if __name__ == "__main__":
    only_download_emails_and_update_database()