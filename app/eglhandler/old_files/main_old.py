import configparser
import os
import shutil

import pandas as pd
from tqdm import tqdm

from eglhandler.src.graph.graph import Graph, EGL
from eglhandler.src.parser import pdf_parser
from eglhandler.src.sqlite.sqlite_db import SqliteDB

def main():
    
    # Set up graph and egl objects
    config = configparser.ConfigParser()
    config.read(['app\eglhandler\settings_azure.ini'])
    azure_settings = config['azure']

    graph: Graph = Graph(azure_settings)
    access_token = graph.generate_access_token(acquire_token_by="username_password")
    headers = graph.create_headers(access_token)
    egl: EGL = EGL(azure_settings, headers)

    # Used with pdf parser to check bodyprevies for terminal names 
    config_pdf_parser = configparser.ConfigParser()
    config_pdf_parser.read(['app\eglhandler\settings_pdf_parser.ini'])

    config_dir_paths = configparser.ConfigParser()
    config_dir_paths.read(['app\eglhandler\settings_directories.ini'])
    dir_paths = config_dir_paths['directories']

    # Constants
    DOWNLOAD_DIR = dir_paths['download_dir']
    PARSED_DIR = dir_paths['parsed_dir']
    DATABASE = dir_paths['database_file']
    DOCUMENTS_DIR = dir_paths['documents_dir']

    # Get email count
    email_count = egl.count_emails_in_folder()

    if email_count == 0:
        print("No emails found in folder.")
        return
    
    print(f"Processing {email_count} emails...")
    
    # Loop through emails, download pdf, parse pdf, import to database
    for count in tqdm(email_count):

        # Downloads pdf from email and gets ID of email
        # The argument is used to find corresponding words in bodypreview
        email_id, terminal_found, pdf_file = egl.download_pdf_from_email(
            config_pdf_parser,
            DOWNLOAD_DIR
            )

        # Parses pdf and gets booking info
        data, same_date, cancellation, terminal = pdf_parser.booking_info(
            DOWNLOAD_DIR,
            pdf_file
            )
        
        # If terminal was not found in pdf_parser, i.e. missing from pdf,
        # use terminal found in email bodypreview, if any
        if not data['tod']:
            data['tod'], terminal = terminal_found
            # Run functions to determine navis voyage again
        
        if data is None:
            continue

        # This is where the booking is sent to the database and handled in Navis
        

        sql_table = SqliteDB(DATABASE)
        cur = sql_table.cursor()

        cur.execute(f"SELECT revised_no from egl_bookings WHERE egl_bookings = {data['booking_no']}")
        booking_exists = cur.fetchone()

        # If booking does not exist and needs to be created then set revised number to 0
        if booking_exists:
            revised_no = booking_exists[0]
        else:
            revised_no = 0

        # Check if pdf name is already in table
        cur.execute(f"SELECT pdf_name from egl_bookings WHERE instr(pdf_name, {data['pdf_name']}) > 0")
        pdf_exists = cur.fetchone()

        cur.execute(f"SELECT booking_no from egl_bookings WHERE booking_no = {data['booking_no']}")
        booking_no = cur.fetchone()


        """ If statments below are used to determine what to do with the booking."""
        if not terminal:
            # If terminal is missing from pdf and bodypreview of e-mail
            print(f"Booking {data['booking_no']} does not have a terminal.")
            egl.move_email_to_folder(email_id, 'no_terminal_folder_id')
            # Do more?

        elif same_date:
            # When booking is updated on the same day as ETD
            print(f"Update for booking {data['booking_no']} received same day as ETD.")
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif pdf_exists:
            # If name of pdf is already in database
            print(f"PDF-file for {data['booking_no']} already exists in database.")
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif cancellation:
            # If cancellation is found in pdf_parser
            if booking_exists:
                # When booking exists it can be removed
                print(f"Deleting booking {data['booking_no']} in Navis.")
                sql_table.delete_booking(data['booking_no'])
                # Delete booking in Navis
            else:
                # If booking does not exist in database, but cancellation is found in pdf_parser
                print(f"Booking {data['booking_no']} should be deleted but does not exist in database.")
                egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif not booking_exists:
            # If booking does not exist in database create it
            print(f"Creating {data['booking_no']} in Navis.")
            sql_table.create_booking(data)
            # Create booking in Navis

        elif revised_no > data['revised_no']:
            # If revised number in pdf_parser is less than in database
            print(f"Revised number in {data['booking_no']} is less than in database.")
            egl.move_email_to_folder(email_id, 'no_change_folder_id')

        elif revised_no < data['revised_no']:
            # If revised number in pdf_parser is greater than in database
            print(f"Updating booking {data['booking_no']} in database and possibly Navis.")
            boolean_dict = sql_table.update_booking(data)
            # Update booking in Navis

        # Moves pdf to new directory 
        shutil.move(
            os.path.join(DOWNLOAD_DIR, pdf_file),
            os.path.join(PARSED_DIR, pdf_file)
            )
        
        df_row = pd.dataframe(data, index=[0])
        df_row.to_csv(os.path.join(DOCUMENTS_DIR, 'booking_info.csv'), mode='a', header=False, index=False)

        print(f"Booking {booking_no} e-mail done. {email_count - count} e-mails remaining.")
        
        
if __name__ == "__main__":
    main()