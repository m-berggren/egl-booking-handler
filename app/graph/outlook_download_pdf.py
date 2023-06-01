import os
from pathlib import Path
import pythoncom
import shutil

import win32com
import win32com.client
import win32ui

EMAIL_ACCOUNT = r"xpf@gsolutions.se"
FOLDER1 = r"Inkorg"
FOLDER2 = r"1. SERVICE"
FOLDER3 = r"SEGOT"
FOLDER4 = r"EVERGREEN"
TO_FOLDER = r"EGL - Database"
IF_NO_VOY = r"EGL - Absent Voyage Navis"
PDF_DIR = r"egl_booking_handler\docs\downloaded_pdfs"
ROOT_DIR = os.path.abspath('')

def outlook_window_exist():
    try:
        win32ui.FindWindow(None, "Microsoft Outlook")
        return True
    except win32ui.error:
        return False
    
def move_to_folder(mail, folder, read_mail=False):
    """
    Creates error sometimes - then needed to remove $USERNAME$\AppData\Local\Temp\gen_py folder.
    """

    try:
        """ Read about it here: https://stackoverflow.com/questions/26764978/using-win32com-with-multithreading/27966218#27966218
        Do yet not grasp the conept.
        """

        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')
        
    except AttributeError:
        home = str(Path.home())
        gen_py_path = os.path.join(home, r"AppData\Local\Temp\gen_py")
        shutil.rmtree(gen_py_path)

        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')

    mapi = out_app.GetNamespace('MAPI')

    to_folder = mapi.Folders[EMAIL_ACCOUNT].Folders[FOLDER1].Folders[FOLDER2].Folders[FOLDER3].Folders[FOLDER4].Folders[folder]

    # Mark mail as read if read_mail is True
    if read_mail:
        mail.UnRead = False
    
    mail.Move(to_folder)

def download_pdf_to_folder(spec_folder=None):
    """
    Creates error sometimes - then need to remove $USERNAME$\AppData\Local\Temp\gen_py folder.
    """

    try:
        """ Read about it here: https://stackoverflow.com/questions/26764978/using-win32com-with-multithreading/27966218#27966218
        Do yet not grasp the conept.
        """

        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')

    except AttributeError:
        home = str(Path.home())
        gen_py_path = os.path.join(home, r"AppData\Local\Temp\gen_py")
        shutil.rmtree(gen_py_path)

        out_app = win32com.client.gencache.EnsureDispatch('Outlook.Application')
    
    mapi = out_app.GetNamespace('MAPI')

    iter_folder = mapi.Folders[EMAIL_ACCOUNT].Folders[FOLDER1].Folders[FOLDER2].Folders[FOLDER3].Folders[FOLDER4]
    save_as_path = PDF_DIR
    mail_count = iter_folder.Items.Count

    if spec_folder:
        iter_folder = iter_folder.Folders[spec_folder]
        mail_count = iter_folder.Items.Count


    if mail_count > 0:

        mail = iter_folder.Items[mail_count]
            
        if '_MailItem' in str(type(mail)):
            if mail.Attachments.Count > 0:
                for attachment in mail.Attachments:
                    if attachment.FileName.startswith('S'):
                        attachment.SaveAsFile(os.path.join(ROOT_DIR, save_as_path, attachment.FileName))
                        return {'filename': attachment.FileName, 'mail': mail, 'mail_count': mail_count}
    else:
        return {'filename': None, 'mail': None, 'mail_count': 0}

                        

if __name__ == '__main__':
    pass
