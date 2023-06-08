import os
import shutil

from tqdm import tqdm

from egl_booking_handler import (
    iterate_outlook_folder_egl,
    pdf_parser, sqlite_db
    )

"""
Only use this to download PDFs and insert them into Database.
Program should otherwise be run from main.py.
"""

ROOT_DIR = os.path.abspath("")
FILE_DIR = os.path.join(ROOT_DIR, "egl_booking_handler\docs\downloaded_pdfs")
PARSED_DIR = os.path.join(ROOT_DIR,"egl_booking_handler\docs\parsed_pdfs")
DATABASE = "egl_booking_handler\sqlite\sqlite_egl.db"



def main():
    conn = sqlite_db.create_connection(DATABASE)

    # Downloads all PDFs in Outlook folder
    iterate_outlook_folder_egl.download_pdfs_in_folder()
    
    # Goes through all PDFs in folder and parses and inserts them into database
    for file in tqdm(os.listdir(FILE_DIR)):
        booking, same_date, cancellation, terminal = pdf_parser.booking_info(FILE_DIR, file)
        if booking is None:
            shutil.move(os.path.join(FILE_DIR, file), os.path.join(PARSED_DIR, file))
            continue
        sqlite_db.execute_sqlite(conn, booking, same_date, cancellation)
        shutil.move(os.path.join(FILE_DIR, file), os.path.join(PARSED_DIR, file))

    conn.close()


if __name__ == '__main__':
    main()