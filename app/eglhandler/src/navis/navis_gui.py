from eglhandler.src.navis.navis_class import NavisGUI
from eglhandler.src.sqlite.sqlite_db import SqliteDB


def create_booking(data: dict, config: dict, database_file: str) -> None:
    """ Create booking
    Check if vessel voyage exist
    if not exist -> export data to file
    if exist -> check if booking exist
    if exist -> update values (but do not use update booking)
    if not exist -> create booking.

    :param data: dict with booking data
    """

    navis = NavisGUI(config)

    if navis.voyage_exist(data['navis_voy']):
        booking_exist = navis.booking_exist(data['booking_no'])
        if booking_exist:
            navis.click_edit_booking(booking_exist)

            # Force update booking does not add hazards at the moment.
            # TODO: add hazards to force update booking
            navis.force_update_booking(data)
        else:
            navis.add_booking(data)
            navis.close_booking_window()
    else:
        voyage_does_not_exist(data, database_file)
        # Used in main function to alert that voyage was not found
        return True

def update_booking(data: dict, bool_dict: dict, config, database_file: str) -> None:
    """ Update booking
    if no True values in bool_dict, exit function.
    Check if vessel voyage exist.
    if not exist -> export data to file.
    if exist -> check if booking exist.
    if exist -> update booking.
    if not exist -> create booking instead of update.

    :param data: dict with booking data
    :param bool_dict: dict with bool values
    """

    navis = NavisGUI(config)

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
        if navis.voyage_exist(data['navis_voy']):
            booking_exist = navis.booking_exist(data['booking_no'])
            if booking_exist:
                if bool_dict['navis_voy'] or bool_dict['tod']:
                    navis.click_edit_booking(booking_exist)
                    navis.update_booking_info(data, bool_dict)

                if bool_dict['count_40hc'] \
                        or bool_dict['count_40dv']\
                        or bool_dict['count_20dv']:
                    navis.click_edit_booking(booking_exist)
                    navis.update_equ_info(data, bool_dict)
                    navis.close_booking_window()
                    
                else:
                    navis.close_booking_window()
                
            else:
                navis.add_booking(data)
        else:
            voyage_does_not_exist(data, database_file)
            
    
def delete_booking(data: dict, config:dict) -> None:
    """ Delete booking
    Check if booking exist
    if exist -> delete booking
    if not exist continue next iteration.

    :param data: dict with booking data
    """
    navis = NavisGUI(config)

    booking_exist = navis.booking_exist(data['booking_no'])
    if booking_exist:
        navis.delete_booking(booking_exist)


def voyage_does_not_exist(data: dict, db_file: str) -> None:
    """Explains that Navis voyage does not exist and moves mail to special folder.
    
    :param data: dict with booking data
    :param db_file: path to database file
    """

    print("\n", f"Voyage {data['navis_voy']} does not exist.")

    # Updates column 'booking_in_navis' for this booking number to 0 (False) in database
    sql = SqliteDB(db_file)
    sql.update_booking(data, booking_in_navis=False)
    

