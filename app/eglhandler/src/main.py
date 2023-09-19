import os
import shutil
from datetime import datetime

import yaml

from eglhandler.src.graph.graph import Graph, EGL
from eglhandler.src.parser import pdf_parser
from eglhandler.src.sqlite.sqlite_db import SqliteDB
from eglhandler.src.navis import navis_gui


def run_main_program():
    """ This program runs from GUI application.
    
    It will:
    1. Download emails from Outlook
    2. Parse pdfs
    3. Import to database
    4. Send to Navis
    5. Update database with Navis info
    6. Move pdfs to parsed folder
    7. Move emails to processed folder

    All bookings handled are saved in a database but also a csv file.
    """

    with open('app\eglhandler\config.yaml', 'r') as _f:
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
    DOCUMENTS_DIR = config['directories'].get('docs')

    # Get email count
    email_count = egl.count_emails_in_folder()

    if email_count == 0:
        print("No email(s) found in folder.")
        return
    
    today = datetime.today().strftime('%Y/%m/%d')
    
    print(f"Processing {email_count} email(s)...\n")
    
    # Loop through emails, download pdf, parse pdf, import to database
    for count in range(email_count):
        
        # Downloads pdf from email and gets ID of email
        # The argument is used to find corresponding words in bodypreview
        email_id, terminal_found, pdf_file = egl.download_pdf_from_email(
            DOWNLOAD_DIR
            )
        
        if pdf_file is None:
            egl.move_email_to_folder(email_id, 'not_for_us_folder_id')
            print(f"No attachment found in e-mail.")
            print(f"{count + 1} of {email_count} e-mail(s).", "\n")
            continue
        
        # Parses pdf and gets booking info
        data, same_date, cancellation, terminal = pdf_parser.booking_info(
            DOWNLOAD_DIR,
            pdf_file,
            config
            )

        if data is None:
            egl.move_email_to_folder(email_id, 'not_for_us_folder_id')
            # Moves pdf to new directory 
            shutil.move(
                os.path.join(DOWNLOAD_DIR, pdf_file),
                os.path.join(PARSED_DIR, pdf_file)
                )
            print(f"PDF-file {pdf_file} are not for us.")
            print(f"{count + 1} of {email_count} e-mail(s).", "\n")
            continue

        # If terminal was not found in pdf_parser, i.e. missing from pdf,
        # use terminal found in email bodypreview, if any
        if not data['tod']:
            data['tod'] = terminal_found
            terminal = terminal_found
            # Run functions to determine navis voyage again
        
        # This is where the booking is sent to the database and handled in Navis
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

        elif today > data['etd']:
            # If ETD is in the past
            print(f"ETD for {data['booking_no']} is in the past.")
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif cancellation:
            # If cancellation is found in pdf_parser
            if booking_exists:
                # When booking exists it can be removed
                print(f"Deleting {data['booking_no']} in Navis.")
                # Delete booking in Navis
                navis_gui.delete_booking(data, config)
                sql_table.update_booking_with_cancellation(data)
                egl.move_email_to_folder(email_id, 'cancel_folder_id')
            else:
                # If booking does not exist in database, but cancellation is found in pdf_parser
                print(f"{data['booking_no']} should be deleted but does not exist in database.")
                sql_table.update_booking_with_cancellation(data)
                egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif not booking_exists:
            # If booking does not exist in database create it
            print(f"Creating {data['booking_no']} in Navis.")
            # Create booking in Navis
            navis_gui.create_booking(data, config, DATABASE)
            sql_table.create_booking(data)
            egl.move_email_to_folder(email_id, 'db_folder_id')

        elif revised_no > int(data['revised_no']):
            # If revised number in pdf_parser is less than in database
            print(f"Revised number in {data['booking_no']} is less than in database.")
            sql_table.update_booking_even_if_lower_revised_no(data)
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif cancellation_exists_in_db:
            """ If cancellation exists in database check if revised number is higher,
            if so, change cancellation status in database and update booking."""

            if revised_no < int(data['revised_no']):
                # Change cancellation status in database and update booking
                print(f"{data['booking_no']} was cancelled but will now be re-created in Navis.")
                navis_gui.create_booking(data, config, DATABASE)
                sql_table.update_booking(data, booking_in_navis=True)
                egl.move_email_to_folder(email_id, 'db_folder_id')
            else:
                # When revised no is less than in database
                print(f"{data['booking_no']} already cancelled in database. Saving PDF file name.")
                sql_table.when_cancellation_exists_in_db()
                egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif revised_no < int(data['revised_no']):
            # If revised number in pdf_parser is greater than in database
            print(f"Updating {data['booking_no']} in database and in Navis if any changes.")
            boolean_dict = sql_table.update_booking(data)
            # Update booking in Navis
            navis_gui.update_booking(data, boolean_dict, config, DATABASE)
            egl.move_email_to_folder(email_id, 'db_folder_id')

        elif revised_no == int(data['revised_no']):
            # If revised number in pdf_parser is equal to in database
            print(f"Revised number in {data['booking_no']} is equal to in database but will update in Navis if any changes.")
            # In case there are changes despite revised no being same, update in Navis too
            navis_gui.update_booking(data, boolean_dict, config, DATABASE)
            sql_table.update_booking(data)
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        # Moves pdf to new directory 
        shutil.move(
            os.path.join(DOWNLOAD_DIR, pdf_file),
            os.path.join(PARSED_DIR, pdf_file)
            )

        print(f"{count + 1} of {email_count} e-mail(s).", "\n")


def run_missing_bookings_in_navis(booking_list: list):
    """ Creates bookings in Navis that are missing due to no active voyage."""

    with open('app\eglhandler\config.yaml', 'r') as _f:
        config = yaml.safe_load(_f)

    DATABASE = config['sqlite'].get('database')

    # Get column names in a list from config file
    db_columns = config['sqlite'].get('db_columns')
    sql_table = SqliteDB(DATABASE)

    print(f"Attempting to create {', '.join(booking_list)} in Navis.")

    for num, booking in enumerate(booking_list):
        values_list = sql_table.get_booking_data(booking)

        created_dict = dict(zip(db_columns, values_list))

        voyage_found = navis_gui.create_booking(created_dict, config, DATABASE)

        # If this is true it means voyage is not found in Navis
        if voyage_found is None:
            print(f"{booking} has not been created.")
            print(f"{len(booking_list) - (num + 1)} booking(s) remaining.")
            continue
        
        else:
            # This will update the booking at column booking_in_navis to 1 (True)
            sql_table.update_values_in_column(
                column='booking_in_navis',
                value='1',
                where_column='booking_no',
                where_value=booking
                )

            print("\n", f"{booking} done.")
            print(f"{len(booking_list) - (num + 1)} booking(s) remaining.")