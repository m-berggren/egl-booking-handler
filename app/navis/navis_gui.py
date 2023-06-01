import pywintypes

import egl_booking_handler.navis_gui_func as nf
from egl_booking_handler.outlook_download_pdf import move_to_folder
import egl_booking_handler.sqlite_db as db

EGL_ABSENT_VOYAGE = 'EGL - Absent Voyage Navis'
EGL_DATABASE = 'EGL - Database'
EGL_CANCELLED = 'EGL - Cancelled'
EGL_NO_CHANGES = 'EGL - No change in Navis'

def create_booking(data_booking, mail) -> None:
    """ Create booking
    Check if vessel voyage exist
    if not exist -> export data to file
    if exist -> check if booking exist
    if exist -> update values (but do not use update booking)
    if not exist -> create booking.
    """

    if nf.voyage_exist(data_booking['navis_voy']):
        booking_exist = nf.booking_exist(data_booking['booking_no'])
        if booking_exist:
            nf.click_edit_booking(booking_exist)
            nf.force_update_booking(data_booking)
        else:
            nf.add_booking(data_booking)
            nf.close_booking_window()
        move_to_folder(mail, EGL_DATABASE, read_mail=False)
    else:
        voyage_does_not_exist(data_booking, mail)

def update_booking(data_booking, bool_dict, mail) -> None:
    """ Update booking
    if no True values in bool_dict, exit function.
    Check if vessel voyage exist.
    if not exist -> export data to file.
    if exist -> check if booking exist.
    if exist -> update booking.
    if not exist -> create booking instead of update.
    """
    bool_list = [bool_dict['navis_voy'],
                 bool_dict['tod'],
                 bool_dict['count_40hc'],
                 bool_dict['count_40dv'],
                 bool_dict['count_20dv']]

    if any(bool_list):        
        if nf.voyage_exist(data_booking['navis_voy']):
            booking_exist = nf.booking_exist(data_booking['booking_no'])
            if booking_exist:
                if bool_dict['navis_voy'] or bool_dict['tod']:
                    nf.click_edit_booking(booking_exist)
                    nf.update_booking_info(data_booking, bool_dict)

                if bool_dict['count_40hc'] \
                        or bool_dict['count_40dv']\
                        or bool_dict['count_20dv']:
                    nf.click_edit_booking(booking_exist)
                    nf.update_equ_info(data_booking, bool_dict)
                    nf.close_booking_window()
                    
                else:
                    nf.close_booking_window()
                
                move_to_folder(mail, EGL_DATABASE, read_mail=False)
            else:
                nf.add_booking(data_booking)
                move_to_folder(mail, EGL_DATABASE, read_mail=False)
        else:
            voyage_does_not_exist(data_booking, mail)

    else:
        move_to_folder(mail, EGL_NO_CHANGES, read_mail=False)
            
    
def delete_booking(data_booking, mail) -> None:
    """ Delete booking
    Check if booking exist
    if exist -> delete booking
    if not exist continue next iteration.
    """

    booking_exist = nf.booking_exist(data_booking['booking_no'])
    if booking_exist:
        nf.delete_booking(booking_exist)
        move_to_folder(mail, EGL_CANCELLED, read_mail=False)


def voyage_does_not_exist(data_booking, mail) -> None:
        """Explains that Navis voyage does not exist and moves mail to special folder.
        """

        lb = "\n"
        print(f"{lb}Voyage {data_booking['navis_voy']} does not exist,{lb}"
                f"{str(data_booking['booking_no'])} is saved to database and moved to {EGL_ABSENT_VOYAGE} folder.")
        
        # Do not want to export data as of now
        #nf.export_data_to_file(data_booking)

        # Updates column 'booking_in_navis' for this booking number to 0 (False) in database
        conn = db.create_connection("egl_booking_handler\sqlite\sqlite_egl.db")
        db.update_values_in_column(conn, 'bookings', 'booking_in_navis', 0, 'booking_no', data_booking['booking_no'])

        try:
            move_to_folder(mail, EGL_ABSENT_VOYAGE, read_mail=False)
        except pywintypes.com_error:
            """Do nothing, cannot copy mail to the same folder.
            This is caused when running 'bookings_on_non_existing_voyage.py'.
            """
            pass
            


if __name__ == '__main__':
    pass


