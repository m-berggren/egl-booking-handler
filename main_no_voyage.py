import os
import shutil
from tkinter import messagebox

from egl_booking_handler.navis_gui_func import get_navis_logo
from egl_booking_handler.outlook_download_pdf import download_pdf_to_folder, outlook_window_exist
from egl_booking_handler import sqlite_db, pdf_parser, navis_gui

def main():

    ROOT_DIR = os.path.abspath('')
    EGL_ABSENT_VOYAGE = 'EGL - Absent Voyage Navis'

    pdf_folder = r"egl_booking_handler\docs\downloaded_pdfs"
    parsed_folder = r"egl_booking_handler\docs\parsed_pdfs"
    file_dir = os.path.join(ROOT_DIR, pdf_folder)
    parsed_dir = os.path.join(ROOT_DIR, parsed_folder)

    database = "sqlite\sqlite_egl.db"
    conn = sqlite_db.create_connection(database)

    if not outlook_window_exist():
        messagebox.showinfo(title="Outlook not found", message="Outlook is not running, please start application and run this file again.")
        exit()

    if not get_navis_logo():
        messagebox.showinfo(title="Navis not found", message="Navis application not found, please start the program.\nIf it is already running please open and minimize it before running this program again.")
        exit()

    counter = 0
    total_mail_count = 0
    lb = "\n"
    running = True

    while running:

        # Gets PDF file and e-mail from Outlook
        pdf_file, mail, mail_count = download_pdf_to_folder(spec_folder=EGL_ABSENT_VOYAGE).values()

        if counter == 0:
            total_mail_count = mail_count
            fixed_mail_count = mail_count
            print(f"{lb}Starting program...{lb}{mail_count} e-mail(s) found in folder.{lb}")

        if fixed_mail_count == 0:
            print(f"{lb}No new e-mail found in folder.{lb}"
                  f"Program is finished.{lb}")
            # f"{lb}{total_mail_count} e-mail(s) downloaded and parsed.{lb}"
            break
            
        # Parses PDF file and returns a tuple with booking info
        booking, same_date, cancellation, terminal = pdf_parser.booking_info(file_dir, pdf_file)

        # Gets latest updated information from database
        dict_for_navis_booking = sqlite_db.get_booking_data(conn, booking)

        # Creates booking in Navis
        navis_gui.create_booking(dict_for_navis_booking, mail)
    
        # Moves pdf to folder
        shutil.move(os.path.join(file_dir, pdf_file), os.path.join(parsed_dir, pdf_file))

        print(f"{counter + 1} of {total_mail_count} e-mail(s) downloaded and parsed.")

        counter += 1
        fixed_mail_count -= 1


if __name__ == '__main__':
    main()

