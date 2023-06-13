from navis import navis_gui_func as nf
from eglhandler.src.navis.navis_gui_class import NavisGUI
from eglhandler.src.sqlite.sqlite_db import SqliteDB


def create_booking(data_booking, mail) -> None:
    """ Create booking
    Check if vessel voyage exist
    if not exist -> export data to file
    if exist -> check if booking exist
    if exist -> update values (but do not use update booking)
    if not exist -> create booking.
    """

    # TODO: add hazards to booking

    if nf.voyage_exist(data_booking['navis_voy']):
        booking_exist = nf.booking_exist(data_booking['booking_no'])
        if booking_exist:
            nf.click_edit_booking(booking_exist)
            nf.force_update_booking(data_booking)
        else:
            nf.add_booking(data_booking)
            nf.close_booking_window()
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

    # TODO: add hazards to booking

    bool_list = [
        bool_dict['navis_voy'],
        bool_dict['tod'],
        bool_dict['count_40hc'],
        bool_dict['count_40dv'],
        bool_dict['count_20dv'],
        bool_dict['hazard_40hc'],
        bool_dict['hazard_40dv'],
        bool_dict['hazard_20dv'],
    ]

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
                
            else:
                nf.add_booking(data_booking)
        else:
            voyage_does_not_exist(data_booking, mail)
            
    
def delete_booking(data_booking, mail) -> None:
    """ Delete booking
    Check if booking exist
    if exist -> delete booking
    if not exist continue next iteration.
    """

    booking_exist = nf.booking_exist(data_booking['booking_no'])
    if booking_exist:
        nf.delete_booking(booking_exist)


def voyage_does_not_exist(data: dict, db_file: str) -> None:
        """Explains that Navis voyage does not exist and moves mail to special folder.
        """

        print('\n', f"Voyage {data['navis_voy']} does not exist.")

        # Updates column 'booking_in_navis' for this booking number to 0 (False) in database
        sql = SqliteDB(db_file)
        sql.update_booking(data, booking_in_navis=False)
            

if __name__ == '__main__':
    pass


