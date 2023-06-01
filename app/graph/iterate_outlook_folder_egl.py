import os
from pathlib import Path
import shutil

import win32com
import win32com.client
import win32ui
from tqdm import tqdm

EMAIL_ACCOUNT = r"xpf@gsolutions.se"
FOLDER1 = r"Inkorg"
FOLDER2 = r"1. SERVICE"
FOLDER3 = r"SEGOT"
FOLDER4 = r"EVERGREEN"
SPECIAL_DOWNLOAD = r"EGL - Special download"
TO_FOLDER = r"EGL - Database"

PDF_DIR = r"egl_booking_handler\docs\downloaded_pdfs"
ROOT_DIR = os.path.abspath('')

def outlook_window_exists():
    try:
        win32ui.FindWindow(None, "Microsoft Outlook")
        return True
    except win32ui.error:
        return False

def download_pdfs_in_folder():
    """
    Loops through all e-mails in a certain folder and downloads
    all PDF attachments locally, then moves that file in Outlook
    to a new folder.
    """

    """
    Creates error sometimes - then needed to remove $USERNAME$\AppData\Local\Temp\gen_py folder.
    """
    try:
        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')
    except AttributeError:
        home = str(Path.home())
        gen_py_path = os.path.join(home, r"AppData\Local\Temp\gen_py")
        shutil.rmtree(gen_py_path)
        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')


    if not outlook_window_exists():
        print("Outlook is not running, please start application and run this file again to download files.")
        exit()

    mapi = out_app.GetNamespace('MAPI')

    iter_folder = mapi.Folders[EMAIL_ACCOUNT].Folders[FOLDER1].Folders[FOLDER2].Folders[FOLDER3].Folders[FOLDER4]
    move_to_folder = iter_folder.Folders[TO_FOLDER]
    iter_folder = iter_folder.Folders[SPECIAL_DOWNLOAD]

    save_as_path = os.path.join(ROOT_DIR, PDF_DIR)

    mail_count = iter_folder.Items.Count

    if mail_count > 0:

        for i in tqdm(range(mail_count, 0, -1), desc='E-mail download counter', unit='E-mails'):
            mail = iter_folder.Items[i]
            
            if '_MailItem' in str(type(mail)):
                
                if mail.Attachments.Count > 0:
                    for attachment in mail.Attachments:
                        if attachment.FileName.startswith('S'):
                            attachment.SaveAsFile(os.path.join(save_as_path, attachment.FileName))

                            mail.UnRead = False

                            try:
                                mail.Move(move_to_folder)
                            except Exception:
                                return None


if __name__ == '__main__':
    pass