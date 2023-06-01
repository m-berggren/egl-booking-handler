import os
import pythoncom
import shutil
from tkinter import messagebox

from egl_booking_handler.navis_gui import create_booking, delete_booking, update_booking
from egl_booking_handler.navis_gui_func import get_navis_logo
from egl_booking_handler.outlook_download_pdf import (download_pdf_to_folder, move_to_folder,
                                                      outlook_window_exist)
from egl_booking_handler import pdf_parser, sqlite_db

ROOT_DIR = os.path.abspath('')
EGL_ABSENT_VOYAGE = 'EGL - Absent Voyage Navis'
EGL_DATABASE = 'EGL - Database'
EGL_CANCELLED = 'EGL - Cancelled'
EGL_NO_TERMINAL_IN_PDF = 'EGL - No terminal in pdf'
EGL_NOT_FOR_US = 'EGL - Not for us'
EGL_NO_CHANGE_IN_NAVIS = 'EGL - No change in Navis'

pdf_folder = r"egl_booking_handler\docs\downloaded_pdfs"
parsed_folder = r"egl_booking_handler\docs\parsed_pdfs"
file_dir = os.path.join(ROOT_DIR, pdf_folder)
parsed_dir = os.path.join(ROOT_DIR, parsed_folder)

database = "egl_booking_handler\sqlite\sqlite_egl.db"
conn = sqlite_db.create_connection(database)

def execute_parser(outlook_id=None):
    """ Main program. Will run until no e-mail is left in mailfolder 'Evergreen'.
    Starts off by downloading pdf from Outlook, parses file, saves into Sqlite3 db,
    creates bookings in program Navis with aid of Pyautogui, and lastly,
    moves the e-mail and the pdf to new folders.

    Aims to handle new bookings, updates and cancellations.
    """


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
        if outlook_id is not None:
            # Initialize COM
            pythoncom.CoInitialize()
            pdf_file, mail, mail_count = download_pdf_to_folder(outlook_id=outlook_id).values()
        else:
            pdf_file, mail, mail_count = download_pdf_to_folder().values()

        if counter == 0:
            total_mail_count = mail_count
            mail_count_loop = mail_count
            print(f"{lb}Starting program...{lb}{mail_count} e-mail(s) found in folder.{lb}")
            if mail_count == 0:
                print(f"Exiting program.{lb}")
                break

        if mail_count_loop == 0:
            print(f"{lb}No new e-mails found in folder.{lb}"
                  f"Program is finished.{lb}")
            # f"{lb}{total_mail_count} e-mail(s) downloaded and parsed.{lb}"
            break
        
        # Parses PDF file
        booking, same_date, cancellation, terminal = pdf_parser.booking_info(file_dir, pdf_file)
        if booking is None:
            shutil.move(os.path.join(file_dir, pdf_file), os.path.join(parsed_dir, pdf_file))
            move_to_folder(mail, EGL_NOT_FOR_US, read_mail=False)
            print(f"E-mail {counter + 1} of {total_mail_count} is not for us.")
            counter += 1
            mail_count_loop -= 1
            continue
        
        # Handles data into Database
        string, booking_no, bool_dict = sqlite_db.execute_sqlite(conn, booking, same_date, cancellation)

        # Navis GUI runs, based on booleans
        if not booking['navis_voy']:
            print(f"Booking {booking['booking_no']} does not have a terminal.")
            move_to_folder(mail, EGL_NO_TERMINAL_IN_PDF, read_mail=False)
        
        elif string == "SAME DATE":
            print(f"Update for booking {booking['booking_no']} received same day as ETD.")
            move_to_folder(mail, EGL_NO_CHANGE_IN_NAVIS, read_mail=False)

        elif string == "PDF EXISTS":
            print(f"PDF-file for {booking['booking_no']} already exists in database.")
            move_to_folder(mail, EGL_NO_CHANGE_IN_NAVIS, read_mail=False)
            
        elif string == "REVISED NO. LESS THAN EXISTING":
            print(f"Revised number in {booking['booking_no']} is less than in database.")
            move_to_folder(mail, EGL_NO_CHANGE_IN_NAVIS, read_mail=False)

        elif string == "REVISED EQUAL TO EXISTING":
            print(f"Revised number in {booking['booking_no']} is equal to in database.")
            move_to_folder(mail, EGL_NO_CHANGE_IN_NAVIS, read_mail=False)

        elif string == "CREATE BOOKING":
            print(f"Creating {booking['booking_no']} in Navis.")
            create_booking(booking, mail)
            
        elif string == "DELETE BOOKING":
            print(f"Deleting booking {booking['booking_no']} in Navis.")
            delete_booking(booking, mail)

        elif string == "SHOULD DELETE BUT BOOKING DOES NOT EXIST":
            print(f"Booking {booking['booking_no']} should be deleted but does not exist in database.")
            move_to_folder(mail, EGL_CANCELLED, read_mail=False)

        elif string == "UPDATE BOOKING":
            print(f"Updating booking {booking['booking_no']} in database and possibly Navis.")
            update_booking(booking, bool_dict, mail)

        else:
            print(f"Booking {booking['booking_no']}. Something went wrong with Navis GUI. Please check the program.")

        shutil.move(os.path.join(file_dir, pdf_file), os.path.join(parsed_dir, pdf_file))

        print(f"{counter + 1} of {total_mail_count} e-mail(s) downloaded and parsed.")

        counter += 1
        mail_count_loop -= 1
        
    if outlook_id is not None:
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    execute_parser()