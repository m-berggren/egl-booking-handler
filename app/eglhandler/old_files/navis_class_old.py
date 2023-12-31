import os
import re
import time
from pathlib import Path

import pyautogui
from pywinauto import Desktop, mouse

from eglhandler.src.navis.navis_dataclass import (
    Navis, Config, transform_navis_dataclass_to_dict)

class NavisGUI:
    """ Class for Navis GUI functions."""
    
    def __init__(self, config:dict) -> None:
        self.navis = Navis(**config['navis'])
        self.config = Config(**transform_navis_dataclass_to_dict(self.navis))
        
        pyautogui.PAUSE = self.navis.gui.pause
        pyautogui.FAILSAFE = self.navis.gui.failsafe
        
        #Checks if Navis is running. If not it will start and log in
        self.get_navis()


    def _grab_navis_window(self):
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
        """Gets Navis window.
        Calls '_grab_navis_window' and '_run_navis' function.

        :return: True if Navis window is found, False if not.
        """


        # Check if Navis window is already open
        if self._grab_navis_window():

            # Looking for error message
            error_found = pyautogui.locateOnScreen(
                image=self.config.connection_error,
                region=self.config.navis_logo_region,
                minSearchTime=0.5,
                grayscale=True,
                confidence=0.8
                )
            
            if error_found:
                x, y = error_found
                pyautogui.click(x + 289, y + 41, duration=0.5)
                time.sleep(2)  # Let error window disappear

                self.run_navis()

                navis_logo_found = pyautogui.locateOnScreen(
                    image=self.config.navis_logo,
                    region=self.config.navis_logo_region,
                    minSearchTime=60,
                    grayscale=True,
                    confidence=0.8
                    )
                if navis_logo_found is None:
                    print('Navis window not found')
                    exit()
                else:
                    self._grab_navis_window()

            
            login_screen_found = pyautogui.locateOnScreen(
                image=self.config.navis_login,
                region=self.config.navis_login_region,
                minSearchTime=30,
                grayscale=True,
                confidence=0.8
                )
            
            if login_screen_found:
                self._log_in_to_navis()

                navis_logo_found = pyautogui.locateOnScreen(
                    image=self.config.navis_logo,
                    region=self.config.navis_logo_region,
                    minSearchTime=60,
                    grayscale=True,
                    confidence=0.8
                    )
            
            navis_logo_found = pyautogui.locateOnScreen(
                image=self.config.navis_logo,
                region=self.config.navis_logo_region,
                minSearchTime=1,
                grayscale=True,
                confidence=0.8
                )

            # Belt and braces check to make sure Navis window is indeed found
            if navis_logo_found is None:
                print('Navis window not found.')
                exit()
            
        # If Navis window is not open, start Navis
        else:
            print('\nNavis not running.\nStarting Navis...')
            self._run_navis()
            self._search_navis_startup_logo(self.config.navis_logo)
            self._grab_navis_window()
        



    def _run_navis(self) -> None:
        """Starts Navis program.
        Called by 'get_navis' function.

        Calls '_log_in_to_navis' function.
        """
        
        navis = self.navis.file.navis_jnlp
        os.startfile(navis)

        find_login_screen = self._find_login_screen(
            login_screen=self.config.navis_login,
            region=self.config.navis_login_region,
            min_search_time=30)
    
        if find_login_screen:
            self._log_in_to_navis()
        else:
            print(f"\nNavis login screen not found.")
            exit()
        

    def _log_in_to_navis(self) -> None:
        """Logs in to Navis.
        Called by '_run_navis' function.
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

        check_voyage_tab = pyautogui.locateCenterOnScreen(
            image=self.config.voyage_tab,
            region=self.config.vessels_and_booking_region,
            minSearchTime=1,
            grayscale=True,
            confidence=0.8
        )
        
        check_voyage_tab_selected = pyautogui.locateCenterOnScreen(
            image=self.config.voyage_tab_selected,
            region=self.config.vessels_and_booking_region,
            minSearchTime=1,
            grayscale=True,
            confidence=0.8
        )
                
        if check_voyage_tab:
            pyautogui.click(check_voyage_tab, duration=0.5)
        elif check_voyage_tab_selected:
            pyautogui.click(check_voyage_tab_selected, duration=0.5)
        else:
            print(f"'VESSELS ACTIVE' tab not found in Navis.")
            exit()

        voyage_field = pyautogui.locateCenterOnScreen(
            image=self.config.voyage_field, 
            region=self.config.voyage_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )

        if voyage_field is None:
            print(f"Error while trying to retrieve field in 'VESSELS ACTIVE'.")
            exit()

        x, y = voyage_field
        pyautogui.click(x - 89, y , duration=0.5)

        with pyautogui.hold('ctrl'):
            pyautogui.press('a')

        pyautogui.press('backspace')
        pyautogui.write(str(value))
        pyautogui.press('enter')
        time.sleep(4)  # Give Navis time to update,
        # may find image for wrong voyage otherwise.

        coordinate_exist = pyautogui.locateOnScreen(
            image=self.config.vessel_exist,
            region= self.config.vessel_exist_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )
        
        if coordinate_exist is None:
            print(f'Voyage {value} not found in Navis.')
            exit()

        return coordinate_exist


    def booking_exist(self, value: str) -> tuple:
        """Checks if booking exist in Navis.
        
        :param value: booking number.
        """

        check_bookings_tab = pyautogui.locateCenterOnScreen(
            image=self.config.bookings_tab,
            region=self.config.vessels_and_booking_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )
        check_bookings_tab_selected = pyautogui.locateCenterOnScreen(
            image=self.config.bookings_tab_selected,
            region=self.config.vessels_and_booking_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )

        if check_bookings_tab is not None:
            pyautogui.click(check_bookings_tab, duration=0.5)
        elif check_bookings_tab_selected is not None:
            pyautogui.click(check_bookings_tab_selected, duration=0.5)
        else:
            print("'BOOKINGS EXPORT' tab not found in Navis.")
            exit()

        time.sleep(0.5)

        booking_field = pyautogui.locateCenterOnScreen(
            image=self.config.booking_field,
            region=self.config.booking_field_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )

        if booking_field is None:
            print("'BOOKINGS EXPORT' field not found in Navis.")
            exit()

        x, y = booking_field
        pyautogui.click(x - 110, y , duration=0.5)

        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
            
        pyautogui.press('backspace')
        pyautogui.write(str(value))
        pyautogui.press('enter')

        # Wait so Navis can update
        time.sleep(3)
        
        # Look for booking if it exists
        coordinate_exist = pyautogui.locateOnScreen(
            image=self.config.booking_exist,
            region=self.config.booking_exist_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
            )

        return coordinate_exist
    

    def add_booking(self, data: dict) -> None:
        """Adds booking to Navis.
        
        :param data: dictionary with booking data.
        """

        add_booking_found = pyautogui.locateCenterOnScreen(
            image=self.config.add_booking,
            region=self.config.add_booking_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
            )
        
        if add_booking_found is None:
            print("Add booking button not found in Navis.")
            exit()
        
        pyautogui.leftClick(add_booking_found, duration=0.5)

        booking_window_found = pyautogui.locateOnScreen(
            image=self.config.booking_window,
            region=self.config.booking_window_region,
            minSearchTime=10,
            grayscale=True,
            confidence=0.8
            )
        
        if booking_window_found is None:
            print("Booking window not found in Navis.")
            exit()

        pyautogui.write(data['booking_no'])
        pyautogui.press('tab')
        time.sleep(1)

        pyautogui.write('EGL')
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(4)

        pyautogui.write(data['navis_voy'])
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(1)
        pyautogui.press('tab')

        pyautogui.write(data['tod'])
        time.sleep(2)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)

        pyautogui.write('XCL')
        pyautogui.press('tab')

        save_booking_found = pyautogui.locateCenterOnScreen(
            image=self.config.save_booking,
            region=self.config.save_booking_region,
            minSearchTime=1,
            grayscale=True,
            confidence=0.8
        )

        if save_booking_found is None:
            print("Save booking button not found in Navis.")
            exit()

        pyautogui.leftClick(save_booking_found, duration=0.5)
        time.sleep(1)

        # [amount of units, sequence no, weight per unit (kg)].
        unit_dict = {
            '45G1': [data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
            '42G1': [data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
            '22G1': [data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]
            }
        
        add_equipment_found = pyautogui.locateCenterOnScreen(
            image=self.config.add_equipment,
            region=self.config.add_equipment_region,
            minSearchTime=1,
            grayscale=True,
            confidence=0.8
            )
        
        if add_equipment_found is None:
            print("Add equipment button not found in Navis.")
            exit()

        # Loop for each type of units, maximum of 3
        for value in unit_dict.values():
            if value[0] == 0:
                continue
            
            # [Unit scope] Presses 'Add' -> 'Add Booking Item'.
            pyautogui.leftClick(
                add_equipment_found,
                duration=0.5
                )
            print(self.config.equ_window)
            print(self.config.equ_window_region)
            print("Trying")
            equ_window_found = pyautogui.locateOnScreen(
                image=self.config.equ_window,
                region=self.config.equ_window_region,
                minSearchTime=10,
                grayscale=True,
                confidence=0.6
            )

            print("Ended")
            
            if equ_window_found is None:
                print("Equipment window not found in Navis.")
                exit()
            
            pyautogui.write(str(value[0]))
            pyautogui.press('tab')
            

            pyautogui.write(str(value[1]))
            pyautogui.press('tab')

            pyautogui.write(str(value[2]))
            pyautogui.press('tab')

            # [Unit scope] locates equ_weight, left clicks box and writes weight
            weight_coord_found = pyautogui.locateOnScreen(
                image=self.config.equ_weight,
                minSearchTime=1,
                grayscale=True,
                confidence=0.8
                )
            
            if weight_coord_found is None:
                print("Weight box not found in Navis.")
                exit()

            pyautogui.leftClick(
                weight_coord_found[0] + 200,
                weight_coord_found[1] + 7,
                duration=0.5
                )
            pyautogui.write(str(value[3]))

            # If there is hazardous information
            if value[4]:
                self.add_hazards_info(value[4])

            save_equ_found = pyautogui.locateCenterOnScreen(
                image=self.config.save_equipment,
                region=self.config.save_equipment_region,
                minSearchTime=1,
                grayscale=True,
                confidence=0.8
                )
            
            if save_equ_found is None:
                print("Save equipment button not found in Navis.")
                exit()
            
            pyautogui.leftClick(
                save_equ_found,
                duration=0.5
                )
            
            pyautogui.locateCenterOnScreen(
                image=self.config.close_equipment,
                region="TODO",
                minSearchTime=1,
                grayscale=True,
                confidence=0.8
                )
            
            if save_equ_found is None:
                print("Close equipment button not found in Navis.")
                exit()

            pyautogui.leftClick(
                save_equ_found,
                duration=0.5
                )


    def force_update_booking(self, data: dict) -> None:
        """Forces update of booking in Navis.
        
        :param data: dictionary with booking data.
        """

        booking_window_found = pyautogui.locateOnScreen(
            image=self.config.booking_window,
            region=self.config.booking_window_region,
            minSearchTime=10,
            grayscale=True,
            confidence=0.8
            )
        
        if booking_window_found is None:
            print("Booking window not found.")
            exit()
        
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(str(data['navis_voy']))
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(str(data['tod']))
        time.sleep(0.2)
        pyautogui.press('tab')


        save_booking_found = pyautogui.locateCenterOnScreen(
            image=self.config.save_booking,
            region=self.config.save_booking_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )

        if save_booking_found is None:
            print("Save booking button not found in Navis.")
            exit()

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

        save_button_found = pyautogui.locateCenterOnScreen(
            image=self.config.save_booking,
            region=self.config.save_booking_region,
            minSearchTime=0.5,
            grayscale=True,
            confidence=0.8
        )

        if save_button_found is None:
            print("Save button not found in Navis.")
            exit()
        
        pyautogui.leftClick(save_button_found, duration=0.5)

        
    def update_booking_info(self, data: dict, bool_dict: dict) -> None:
        """Updates booking info in Navis.
        
        :param data: dictionary with booking data.
        :param bool_dict: dictionary with boolean values.
        """

        time.sleep(4)
        if bool_dict['navis_voy']:
            # Finds vessel voyage.
            pyautogui.leftClick(self.coordinate.get('vessel_visit'), duration=0.5)
            with pyautogui.hold('ctrl'):
                pyautogui.press('a')
            pyautogui.press('backspace')
            pyautogui.write(str(data['navis_voy']))
            pyautogui.press('tab')
            time.sleep(2)

        if bool_dict['tod']:
            # Finds tod.
            pyautogui.leftClick(
                self.coordinate.get('terminal_of_discharge'),
                duration=0.5
                )
            with pyautogui.hold('ctrl'):
                pyautogui.press('a')
            pyautogui.press('backspace')
            pyautogui.write(str(data['tod']))
            pyautogui.press('tab')
            time.sleep(2)

        # [Booking scope] Presses 'Save' to save booking.
        pyautogui.leftClick(
            self.coordinate.get('save_booking'),
            duration=0.5
            )
        time.sleep(2)
    

    def _check_and_handle_delete_equ_error(self):
        """Checks for error message and handles it if found."""

        
        
        coord = pyautogui.locateOnScreen(
            image=self.config.error_gated_in,
            minSearchTime=2,
            region=self.config.error_gated_in_region
            )
        if coord:
            pyautogui.leftClick(
                self.coordinate.get('error_message_click_ok'),
                duration=0.5
                )


    def check_and_handle_equ_update_error(self):
        """Checks for error message and handles it if found."""

        
        
        coord = pyautogui.locateOnScreen(
            image=self.config.error_less_than_gated_in,
            minSearchTime=2,
            region=self.config.error_less_than_gated_in_region
            )
        if coord:
            # Click 'OK' on error message.
            pyautogui.leftClick(
                self.coordinate.get('error_message_click_ok'),
                duration=0.5
                )
            # Click 'Cancel' [Unit scope]
            pyautogui.leftClick(
                self.coordinate.get('cancel_equipment_window'),
                duration=0.5
                )
            # Confirm 'Yes'
            pyautogui.leftClick(
                self.coordinate('confirm_cancel_equipment'),
                duration=0.5
                )


    def confirm_delete_units(self):
        """Confirms deletion of units."""

        pyautogui.leftClick(
            self.coordinate.get('confirm_deleting_unit'),
            duration=0.5
            )


    def update_equ_info(self, data: dict, bool_dict: dict) -> None:
        """Updates equipment info in Navis.
        
        :param data: dictionary with booking data.
        :param bool_dict: dictionary with boolean values.
        """

        time.sleep(4)
        

        # [boolean, image, amount of units, sequence no, equ type, weight per unit (kg), hazard].
        unit_dict = {
            '45G1': [bool_dict['count_40hc'], self.config.image_40hc, data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
            '42G1': [bool_dict['count_40dv'], self.config.image_40dv, data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
            '22G1': [bool_dict['count_20dv'], self.config.image_20dv, data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]
            }
        
        for unit in unit_dict.values():
            if unit[0]:  # If changes to unit type
                coord = pyautogui.locateOnScreen(
                    image=unit[1],
                    minSearchTime=3,
                    region=self.config.equipment_search_region
                    )
                
                if unit[2] == 0:  # If data is 0 then delete row
                    pyautogui.rightClick(coord, duration=0.5)
                    pyautogui.move(xOffset=42, yOffset=65, duration=0.5)
                    pyautogui.leftClick()
                    self.confirm_delete_units()
                    self._check_and_handle_delete_equ_error()

                elif not coord:  # If image is not found
                    # [Unit scope] Presses 'Add' -> 'Add Booking Item'.
                    
                    pyautogui.leftClick(
                        self.coordinate.get('add_equipment'),
                        duration=0.5
                        )
                    time.sleep(4)

                    pyautogui.write(str(unit[2]))
                    pyautogui.press('tab')

                    pyautogui.write(str(unit[3]))
                    pyautogui.press('tab')

                    pyautogui.write(str(unit[4]))
                    pyautogui.press('tab')

                    weight_coord = pyautogui.locateOnScreen(
                        image=self.config.equ_weight,
                        minSearchTime=3
                        )
                    pyautogui.leftClick(
                        weight_coord[0] + 200,
                        weight_coord[1] + 4,
                        duration=0.5
                        )
                    pyautogui.write(str(unit[5]))

                    # If there is hazardous information
                    if unit[6]:
                        self.add_hazards_info(unit[6])

                    # [Unit scope] Presses 'Save' to save unit and then 'Close'.
                    pyautogui.leftClick(
                        self.coordinate.get('save_equipment'),
                        duration=0.5
                        )
                    time.sleep(3)
                    pyautogui.move(xOffset=45, yOffset=0, duration=0.2)
                    pyautogui.leftClick()
                    time.sleep(3)

                else:
                    pyautogui.rightClick(coord, duration=0.5)
                    pyautogui.move(xOffset=10, yOffset=10, duration=0.5)
                    pyautogui.leftClick()
                    time.sleep(4)

                    pyautogui.write(str(unit[2]))
                    pyautogui.press('tab')

                    # [Unit scope] Presses 'Save' to save unit.
                    pyautogui.leftClick(
                        self.coordinate.get('save_equipment'),
                        duration=0.5
                        )

                    # Check for error message (when containers set are less than what is delivered).
                    self.check_and_handle_equ_update_error()


    def delete_booking(self, coordinates):
        """Deletes booking in Navis.
        Checks for error message from '_check_and_handle_delete_equ_error'.

        :param coordinates: tuple with coordinates of booking.
        """

        time.sleep(3)   # Navis may need some extra time to refresh properly.
        pyautogui.rightClick(coordinates, duration=0.5)
        pyautogui.move(xOffset=24, yOffset=60, duration=0.5)
        pyautogui.leftClick()
        pyautogui.leftClick(
            self.coordinate.get('confirm_deleting_unit'),
            duration=0.5
            )

        # Check for error message (when containers are collected or gated in).
        self._check_and_handle_delete_equ_error()


    def add_hazards_info(self, string: str) -> None:
        """Adds hazardous information to unit.
        
        :param string: string with hazardous information.

        example string: '3/1234, 8/8491, 9/6790'
        """
        
        # String value is in the format '3/1234' and we only want '1234'
        list_of_hazards = re.findall(r"\d{4}", string)

        for num, hazard in enumerate(list_of_hazards):
            # First loop needs to do the more work
            if num == 0:
                pyautogui.leftClick(
                    self.coordinate.get('add_hazard_button'),
                    duration=0.5
                    )
                
                time.sleep(2)

                pyautogui.leftClick(
                    self.coordinate.get('add_unnr_plus_sign'),
                    duration=0.5
                    )
                pyautogui.write(hazard)
                pyautogui.press('tab')

                pyautogui.leftClick(
                    self.coordinate.get('add_unnr_to_unit'),
                    duration=0.5
                    )
                
            # After first look only needs to add unnr
            if num > 0:
                pyautogui.write(hazard)
                pyautogui.press('tab')

                pyautogui.leftClick(
                    self.coordinate.get('add_unnr_to_unit'),
                    duration=0.5
                    )
        
        # Save and close hazard window
        pyautogui.leftClick(
            self.coordinate.get('close_hazard_window'),
            duration=0.5
            )
        time.sleep(1)
