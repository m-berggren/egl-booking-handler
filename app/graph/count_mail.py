import os
from pathlib import Path
import pythoncom
import shutil

import win32com
import win32com.client
import win32ui

def outlook_window_exists() -> bool:
    try:
        win32ui.FindWindow(None, "Microsoft Outlook")
        return True
    except win32ui.error:
        return False
    

def count_evergreen_bookings(outlook_id=None) -> int:
    """ Counts the number of e-mails in the Evergreen folder. """

    EMAIL_ACCOUNT = r"xpf@gsolutions.se"
    FOLDER1 = r"Inkorg"
    FOLDER2 = r"1. SERVICE"
    FOLDER3 = r"SEGOT"
    EVERGREEN = r"EVERGREEN"

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
    iter_folder = mapi.Folders[EMAIL_ACCOUNT].Folders[FOLDER1].Folders[FOLDER2].Folders[FOLDER3].Folders[EVERGREEN]

    return iter_folder.Items.Count
        



