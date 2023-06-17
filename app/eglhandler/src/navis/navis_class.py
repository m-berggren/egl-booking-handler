import inspect
import os
import re
import sys
import time
from typing import Literal

import pyautogui
from pywinauto import Desktop, mouse

from eglhandler.src.navis.navis_dataclass import (
    Navis, Config, transform_navis_dataclass_to_dict)
from eglhandler.src.navis.image_identifier import get_mouse_coords

class NavisGUI:
    """ Class for Navis GUI functions."""
    
    def __init__(self, config:dict) -> None:
        self.navis = Navis(**config['navis'])
        self.config = Config(**transform_navis_dataclass_to_dict(self.navis))
        
        pyautogui.PAUSE = self.navis.gui.pause
        pyautogui.FAILSAFE = self.navis.gui.failsafe

        # Set waiting time for Navis to load (s)
        self.wait_for_vessel = 6
        self.wait_for_booking = 5
        self.wait_for_vessel_visit = 6
        self.wait_for_tod = 3
        
        #Checks if Navis is running. If not it will start and log in
        self.get_navis()


    def grab_navis_window(self):
        """ Sets Navis window in front of all other windows.
        Called by 'get_navis' function.
        
        :return: True if Navis window is found, False if not.
        """

        windows = Desktop(backend='win32').windows()
        for window in windows:
            if "navis n4" in window.window_text().lower():
                window.set_focus()
                window.move_window(x=500, y=0, width=int(1425), height=1045)
                mouse.move(coords=(int(1920/4), int(1080/2)))
                return True
        return False
    

    def get_navis(self) -> None:
        """Gets Navis window."""

        # If Navis is not running, start Navis and check for Navis logo
        if not self.grab_navis_window():
            print('\nNavis not running.\nStarting Navis...')
            self.run_navis()
            self.grab_navis_window()
            return
        
        # If error found, click 'OK' and restarts Navis,
        # then check for Navis logo. If not found restart process again
        self.handle_connection_error_window()

        # If Navis login window found, log in to Navis and
        # check for Navis logo, if not found restart process again
        self.handle_login_window()
        return


    def run_navis(self) -> None:
        """Starts Navis program and looks for login screen"""
        
        navis = self.navis.file.navis_jnlp
        os.startfile(navis)

        # Check for login window
        login_screen_found = get_mouse_coords(self.config.navis_login, duration=30)
    
        if login_screen_found is None:
            print(f"\nNavis login screen not found.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        self.log_in_to_navis()

        navis_window_found = get_mouse_coords(self.config.navis_logo, duration=60)
        if navis_window_found is None:
            print(f"\nNavis window not found by program.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        self.grab_navis_window()
        return


    def handle_connection_error_window(self) -> None:
        """ Checks if error message found."""

        error_found = get_mouse_coords(self.config.connection_error, duration=0.5)
        if error_found is None:
            return
        
        # When error found, click 'OK' and start Navis program
        x, y = error_found
        pyautogui.click(x + 289, y + 41, duration=0.5)  # Let error window disappear
        time.sleep(1)
        self.run_navis()
        return
    
    
    def handle_login_window(self) -> None:
        """ Check if login window found."""

        # Searches for login window, if not found return
        login_screen_found = get_mouse_coords(self.config.navis_login, duration=0.5)
        if login_screen_found is None:
            return
        
        # If login window found then log in to Navis and check for Navis logo
        self.log_in_to_navis()
        navis_logo_found = get_mouse_coords(self.config.navis_logo, duration=60)
        if navis_logo_found is None:
            print('Navis window not found.')
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        self.grab_navis_window()
        return
    

    def log_in_to_navis(self) -> None:
        """Logs in to Navis.
        Called by 'run_navis' function.
        """
        pyautogui.PAUSE = 0.1

        pyautogui.write(self.navis.login.user)
        pyautogui.press('tab')
        pyautogui.write(self.navis.login.password)
        pyautogui.press('enter')

        pyautogui.PAUSE = self.navis.gui.pause
        

    def voyage_exist(self, value: str) -> tuple:
        """Checks if voyage exist in Navis.
        
        :param value: voyage number.
        """

        # Searches for voyage tab, click it if found
        voyage_tab_found = get_mouse_coords(
            [self.config.voyage_tab, self.config.voyage_tab_selected]
            , duration=1
        )
        if voyage_tab_found is None:
            print(f"'VESSELS ACTIVE' tab not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        pyautogui.click(voyage_tab_found, duration=0.5)

        # Searches for voyage field, click it if found
        voyage_field_found = get_mouse_coords(self.config.voyage_field, duration=5)
        if voyage_field_found is None:
            print(f"'Voyage' field not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            
        x, y = voyage_field_found
        pyautogui.click(x - 89, y , duration=0.5)

        # And then write voyage number into the field
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')

        pyautogui.press('backspace')
        pyautogui.write(str(value))
        pyautogui.press('enter')

        # Time to sleep is set at init of class
        time.sleep(self.wait_for_vessel)  # Give Navis time to update,
        # may find image for wrong voyage otherwise.

        # Searches for vessel in Navis, return coordinates if found
        vessel_found = get_mouse_coords(self.config.vessel_exist, duration=1)
        if vessel_found is None:
            return None
        
        return vessel_found


    def booking_exist(self, value: str) -> tuple:
        """Checks if booking exist in Navis.
        
        :param value: booking number.
        """

        # Searches for bookings tab, click it if found
        booking_tab_found = get_mouse_coords(
            [self.config.bookings_tab, self.config.bookings_tab_selected],
            duration=5
        )
        if booking_tab_found is None:
            print("'BOOKINGS EXPORT' tab not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.click(booking_tab_found, duration=0.5)
        time.sleep(0.5)

        # Searches for booking field, click it if found
        booking_field_found = get_mouse_coords(self.config.booking_field, duration=5)
        if booking_field_found is None:
            print("'BOOKINGS EXPORT' field not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        x, y = booking_field_found
        pyautogui.click(x - 110, y , duration=0.5)

        # And then write booking number into the field
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
            
        pyautogui.press('backspace')
        pyautogui.write(str(value))
        pyautogui.press('enter')

        # Time to sleep is set at init of class
        time.sleep(self.wait_for_booking)  
        
        # Searches for booking in Navis, return coordinates if found
        booking_found = get_mouse_coords(self.config.booking_exist, duration=5)
        if booking_found is None:
            return None

        return booking_found
    

    def add_booking(self, data: dict) -> None:
        """Adds booking to Navis.
        
        :param data: dictionary with booking data.
        """

        # Searches for add booking button, click it if found
        add_booking_found = get_mouse_coords(self.config.add_booking, duration=5)        
        if add_booking_found is None:
            print("Add booking button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.leftClick(add_booking_found, duration=0.5)

        # Searches for booking window, write booking number if found
        booking_window_found = get_mouse_coords(self.config.vessel_visit_booking_window, duration=50)
        if booking_window_found is None:
            print("Booking window not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        time.sleep(0.1)
        pyautogui.write(data['booking_no'])
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.write('EGL')
        time.sleep(1)
        pyautogui.press('tab')

        # Time to sleep is set at init of class
        time.sleep(self.wait_for_vessel_visit)
        pyautogui.write(data['navis_voy'])
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('tab')

        # Time to sleep is set at init of class
        time.sleep(self.wait_for_tod)
        pyautogui.write(data['tod'])
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write('XCL')
        time.sleep(0.5)
        pyautogui.press('tab')
        

        save_booking_found = get_mouse_coords(self.config.save_booking, duration=5)
        if save_booking_found is None:
            print("Save booking button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        pyautogui.leftClick(save_booking_found, duration=0.5)
        time.sleep(1)

        # {unit type: [amount of units, sequence no, weight per unit (kg)]}.
        unit_dict = {
            '45G1': [data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
            '42G1': [data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
            '22G1': [data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]
            }
        
        # Searches for add equipment button, will be clicked later in loop below
        add_equipment_found = get_mouse_coords(self.config.add_equipment, duration=5)
        
        if add_equipment_found is None:
            print("Add equipment button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        # Loop for each type of units, max is 3 iterations
        for value in unit_dict.values():
            if value[0] == 0:
                continue
            
            # Click add equipment button
            pyautogui.leftClick(add_equipment_found, duration=0.5)
      
            # Searches for equipment window, writes out values if found
            equ_window_found = get_mouse_coords(self.config.equ_window, duration=10)
            
            if equ_window_found is None:
                print("Equipment window not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()               
            
            time.sleep(2)
            pyautogui.write(str(value[0]))
            time.sleep(1)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.write(str(value[1]))
            time.sleep(1)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.write(str(value[2]))
            time.sleep(1)
            pyautogui.press('tab')
            time.sleep(0.3)

            # Search for weight box, click it and write out weight
            equ_weight_found = get_mouse_coords(self.config.equ_weight, duration=5)
            if equ_weight_found is None:
                print("Weight box not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()
                
            pyautogui.leftClick(
                equ_weight_found[0] + 250,
                equ_weight_found[1],
                duration=0.3
                )
            pyautogui.write(str(value[3]))

            # If there is hazardous information
            if value[4]:
                self.add_hazards_info(value[4])

            # Searches for save equipment, clicks it if found
            save_equ_found = get_mouse_coords(self.config.save_equipment, duration=1)
            if save_equ_found is None:
                print("Save equipment button not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()
            
            pyautogui.leftClick(save_equ_found, duration=0.5)
            time.sleep(0.5)
            # Close equipment window
            pyautogui.leftClick(
                x=save_equ_found[0] + 50,
                y=save_equ_found[1],
                duration=0.3
            )
            time.sleep(1)


    def force_update_booking(self, data: dict) -> None:
        """Forces update of booking in Navis.
        
        :param data: dictionary with booking data.
        """

        # Searches for booking window
        booking_window_found = get_mouse_coords(self.config.vessel_visit_booking_window, duration=10)
        if booking_window_found is None:
            print("Booking window not found.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.press('tab')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(2)
        pyautogui.write(str(data['navis_voy']))
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(2)
        pyautogui.write(str(data['tod']))
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.5)

        # Searches for save booking button
        save_booking_found = get_mouse_coords(self.config.save_booking, duration=5)
        if save_booking_found is None:
            print("Save booking button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.leftClick(save_booking_found, duration=0.5)


    def click_edit_booking(self, coordinates: pyautogui.Point):
        """Clicks 'Edit Booking' on booking in Navis.
        
        :param coordinates: tuple with coordinates of booking.
        """
        
        pyautogui.rightClick(coordinates, duration=0.5)
        pyautogui.move(xOffset=10, yOffset=10)
        pyautogui.leftClick(duration=0.5)


    def close_booking_window(self):
        """Closes booking window in Navis."""

        # Searches for close button
        close_button_found = get_mouse_coords(self.config.close_window, duration=5)
        if close_button_found is None:
            print("Save button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.leftClick(close_button_found, duration=0.5)

        
    def update_booking_info(self, data: dict, bool_dict: dict) -> None:
        """Updates booking info in Navis.
        
        :param data: dictionary with booking data.
        :param bool_dict: dictionary with boolean values.
        """

        # Search and validate booking window
        booking_window_found = get_mouse_coords(self.config.vessel_visit_booking_window, duration=10)
        if booking_window_found is None:
            print("Booking window not found.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        if bool_dict['navis_voy']:
            # Finds vessel voyage and writes out new voyage
            vessel_visit_found = get_mouse_coords(self.config.vessel_visit_booking_window, duration=5)
            if vessel_visit_found is None:
                print("Vessel visit box not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()
            
            pyautogui.leftClick(
                x=vessel_visit_found[0] + 230,
                y=vessel_visit_found[1],
                duration=0.2
                )

            with pyautogui.hold('ctrl'):
                pyautogui.press('a')
            pyautogui.press('backspace')
            pyautogui.write(str(data['navis_voy']))
            pyautogui.press('tab')
            

        if bool_dict['tod']:
            # Finds tod and writes out new tod
            tod_found = get_mouse_coords(self.config.tod_booking_window, duration=5)
            if tod_found is None:
                print("TOD box not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()
            
            pyautogui.leftClick(
                x=tod_found[0] + 250,
                y=tod_found[1],
                duration=0.2
                )
            
            with pyautogui.hold('ctrl'):
                pyautogui.press('a')
            pyautogui.press('backspace')
            pyautogui.write(str(data['tod']))
            pyautogui.press('tab')

        # Search for save button and click it
        save_booking_found = get_mouse_coords(self.config.save_booking, duration=5)
        if save_booking_found is None:
            print("Save booking button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.leftClick(save_booking_found, duration=0.5)
    

    def check_and_handle_delete_equ_error(self, action: Literal['check', 'handle']='check') -> None:
        """Checks for error message.
        
        :param action: action to take if error message is not found.
        """
  
        # Searches for error message
        error_message_found = get_mouse_coords(self.config.error_gated_in, duration=0.5)
        if error_message_found is None:
            if action == 'check':
                return
            elif action == 'handle':
                print("Error message not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()
            else:
                return
        
        # Will click 'OK' on error message
        pyautogui.leftClick(
            x=error_message_found[0] + 422,
            y=error_message_found[1] + 181,
            duration=0.5
            )
        return


    def check_and_handle_equ_update_error(self) -> None:
        """Checks for error message and handles it if found."""

        # Search for error message
        error_message_found = get_mouse_coords(self.config.error_less_than_gated_in, duration=0.5)
        if error_message_found is None:
            return
        
        # Will click 'OK' on error message
        pyautogui.leftClick(
            x=error_message_found[0] + 422,
            y=error_message_found[1] + 181,
            duration=0.5
            )
        
        # Search for cancel button in equipment window and click it
        equ_cancel_button_found = get_mouse_coords(self.config.equ_cancel_button, duration=5)
        if equ_cancel_button_found is None:
            print("Cancel button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.leftClick(equ_cancel_button_found, duration=0.5)

        # Search for 'Yes' button in confirmation window and click it
        confirm_cancel_found = get_mouse_coords(self.config.equ_confirm_cancel, duration=5)
        if confirm_cancel_found is None:
            print("Confirm cancel button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        
        pyautogui.leftClick(confirm_cancel_found, duration=0.5)
        return


    def confirm_delete_units(self):
        """Confirms deletion of units."""

        # Search for 'Yes' button in confirmation window and click it
        equ_confirm_delete_found = get_mouse_coords(self.config.equ_confirm_cancel, duration=0.5)
        if equ_confirm_delete_found is None:
            return
    
        pyautogui.leftClick(equ_confirm_delete_found, duration=0.5)
        return
        

    def update_equ_info(self, data: dict, bool_dict: dict) -> None:
        """Updates equipment info in Navis.
        
        :param data: dictionary with booking data.
        :param bool_dict: dictionary with boolean values.
        """        

        # {unit type: [boolean, image, amount of units, sequence no, equ type, weight per unit (kg), hazard]}
        unit_dict = {
            '45G1': [bool_dict['count_40hc'], self.config.image_40hc, data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
            '42G1': [bool_dict['count_40dv'], self.config.image_40dv, data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
            '22G1': [bool_dict['count_20dv'], self.config.image_20dv, data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]
            }
        
        for unit in unit_dict.values():
            if unit[0]:  # If there are changes to unit type

                unit_image_found = get_mouse_coords(unit[1], duration=0.5)
                                                
                if unit[2] == 0:  # If data is 0 then delete row
                    pyautogui.rightClick(unit_image_found, duration=0.5)
                    pyautogui.move(xOffset=42, yOffset=65, duration=0.5)
                    pyautogui.leftClick()
                    self.confirm_delete_units()
                    self.check_and_handle_delete_equ_error()

                # If image is not found will add unit
                elif unit_image_found is None:
                    # Search for 'Add equipment' button and click it
                    add_equipment_found = get_mouse_coords(self.config.add_equipment, duration=5)
                    if add_equipment_found is None:
                        print("Add equipment button not found in Navis.")
                        print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                        sys.exit()
                    
                    pyautogui.leftClick(add_equipment_found, duration=0.5)

                    # Search and validate equipment window
                    equ_window_found = get_mouse_coords(self.config.equ_window, duration=10)
                    if equ_window_found is None:
                        print("Equipment window not found in Navis.")
                        print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                        sys.exit()       

                    pyautogui.write(str(unit[2]))
                    pyautogui.press('tab')

                    pyautogui.write(str(unit[3]))
                    pyautogui.press('tab')

                    pyautogui.write(str(unit[4]))
                    pyautogui.press('tab')

                    # Search for weight box and write weight
                    equ_weight_found = get_mouse_coords(self.config.equ_weight, duration=5)
                    if equ_weight_found is None:
                        print("Weight box not found in Navis.")
                        print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                        sys.exit()
                
                    pyautogui.leftClick(
                        equ_weight_found[0] + 200,
                        equ_weight_found[1] + 7,
                        duration=0.5
                        )
                    pyautogui.write(str(unit[5]))

                    # If there is hazardous information
                    if unit[6]:
                        self.add_hazards_info(unit[6])

                    # Searches for save equipment, clicks it if found
                    save_equ_found = get_mouse_coords(self.config.save_equipment, duration=5)
                    if save_equ_found is None:
                        print("Save equipment button not found in Navis.")
                        print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                        sys.exit()
                    
                    pyautogui.leftClick(save_equ_found, duration=0.5)
                    time.sleep(0.5)
                    # Closes equipment window
                    pyautogui.leftClick(
                        x=save_equ_found[0] + 50,
                        y=save_equ_found[1],
                        duration=0.3
                    )

                # If image is found will update unit
                else:
                    pyautogui.rightClick(unit_image_found, duration=0.5)
                    pyautogui.move(xOffset=10, yOffset=10, duration=0.5)
                    pyautogui.leftClick()

                    # Search and validate equipment window
                    equ_window_found = get_mouse_coords(self.config.equ_window, duration=10)
                    if equ_window_found is None:
                        print("Equipment window not found in Navis.")
                        print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                        sys.exit()

                    pyautogui.write(str(unit[2]))
                    pyautogui.press('tab')

                    # Searches for save equipment, clicks it if found
                    save_equ_found = get_mouse_coords(self.config.save_equipment, duration=5)
                    if save_equ_found is None:
                        print("Save equipment button not found in Navis.")
                        print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                        sys.exit()
                    
                    pyautogui.leftClick(save_equ_found, duration=0.5)
                    time.sleep(0.5)
                    # Closes equipment window
                    pyautogui.leftClick(
                        x=save_equ_found[0] + 50,
                        y=save_equ_found[1],
                        duration=0.3
                    )

                    # Check for error message (when containers set are less than what is delivered).
                    self.check_and_handle_equ_update_error()


    def delete_booking(self, coordinates):
        """Deletes booking in Navis.
        Checks for error message from 'check_and_handle_delete_equ_error'.

        :param coordinates: tuple with coordinates of booking.
        """

        time.sleep(3)   # Navis may need some extra time to refresh properly.
        pyautogui.rightClick(coordinates, duration=0.5)
        pyautogui.move(xOffset=24, yOffset=60, duration=0.5)
        pyautogui.leftClick()

        # Search for 'Delete Booking' confirmation message.
        delete_booking_confirmation_found = get_mouse_coords(self.config.delete_booking, duration=5)
        if delete_booking_confirmation_found is None:
            print("Delete booking message confirmation not found.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        pyautogui.leftClick(delete_booking_confirmation_found, duration=0.5)

        # Check for error message (when containers are collected or gated in).
        self.check_and_handle_delete_equ_error(action='handle')


    def add_hazards_info(self, string: str) -> None:
        """Adds hazardous information to unit.
        
        :param string: string with hazardous information.

        example string: '3/1234, 8/8491, 9/6790'
        """
        
        # String value is in the format '3/1234' and we only want '1234'
        list_of_hazards = re.findall(r"\d{4}", string)

        for num, hazard in enumerate(list_of_hazards):
            # First loop needs to do most of the work
            if num == 0:
                # Search for hazards button, ckick it if found
                hazards_button_found = get_mouse_coords(self.config.hazards_button, duration=5)
                if not hazards_button_found:
                    print("Hazard button not found in Navis.")
                    print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                    sys.exit()

                pyautogui.leftClick(hazards_button_found, duration=0.5)

                # Searches for hazards window, if found continues
                hazards_window_found = get_mouse_coords(self.config.hazards_window_check, duration=5)
                if not hazards_window_found:
                    print("Hazard window not found in Navis.")
                    print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                    sys.exit()

                # Searches for add button, if found clicks it and writes unno info
                hazards_button_add_found = get_mouse_coords(self.config.hazards_button_add, duration=5)
                if not hazards_button_add_found:
                    print("Hazards add button not found in Navis.")
                    print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                    sys.exit()

                pyautogui.leftClick(hazards_button_add_found, duration=0.5)
                time.sleep(0.5)
                pyautogui.write(hazard)
                time.sleep(0.5)
                pyautogui.press('tab')
                time.sleep(0.5)

                hazards_button_add_unno_found = get_mouse_coords(self.config.hazards_button_add_unno, duration=5)
                if not hazards_button_add_unno_found:
                    print("Hazards add unnr button not found in Navis.")
                    print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                    sys.exit()

                pyautogui.leftClick(hazards_button_add_unno_found, duration=0.5)
                
            # After first loop will only needs to add unnr
            if num > 0:
                time.sleep(0.5)
                pyautogui.write(hazard)
                time.sleep(0.5)
                pyautogui.press('tab')
                time.sleep(0.5)

                pyautogui.leftClick(hazards_button_add_unno_found, duration=0.5)
        
        # Search for save hazards button to close window
        hazards_save_button_found = get_mouse_coords(self.config.hazards_save_button, duration=5)
        if not hazards_save_button_found:
            print("Hazards save button not found in Navis.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()

        pyautogui.leftClick(hazards_save_button_found, duration=0.5)
        time.sleep(0.5)
