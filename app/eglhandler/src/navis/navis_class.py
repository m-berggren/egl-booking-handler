import os
import re
import time
from pathlib import Path

import pyautogui
from pywinauto import Desktop, mouse

class NavisGUI:
    """Class for Navis GUI functions."""

    def __init__(self, config:dict) -> None:
        self.config = config.get('navis')
        self.png = self.config.get('png')
        self.coordinate = self.config.get('coordinate')
        self.region = self.config.get('region')
        self.login = self.config.get('login')
        self.file = self.config.get('file')

        # Sets the overall delay between every PyAutoGUI call.
        pyautogui.PAUSE = self.config['gui'].get('pause')

        # Sets a failsafe for PyAutoGUI. If the mouse cursor is in the upper left corner
        pyautogui.FAILSAFE = self.config['gui'].get('failsafe')
        
        #Checks if Navis is running. If not it will start and log in
        self.get_navis()
            
            
    def _grab_navis_window(self):
        """Sets Navis window in front of all other windows.
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

        NAVIS_LOGO = self.png['startup'].get('navis_logo')
        LOGO_REGION = tuple([int(i) for i in self.region.get('navis_logo')])  #x, y, width, height
        INITIAL_LOGO_REGION = tuple([int(i) for i in self.region.get('initial_navis_logo')])  #x, y, width, height
        CONNECTION_ERROR = self.png['startup'].get('connection_error')

        # Check if Navis window is already open.
        if self._grab_navis_window():
            navis_logo_found = pyautogui.locateOnScreen(
                image=NAVIS_LOGO,
                region=LOGO_REGION,
                minSearchTime=2)

            # Belt and braces check to make sure Navis window is indeed found.
            if navis_logo_found:
                return
            
            # Looking for error message
            error_found = pyautogui.locateCenterOnScreen(
                image=CONNECTION_ERROR,
                minSearchTime=2
                )
            
            if error_found:
                x, y = error_found
                pyautogui.click(x + 289, y + 41, duration=0.5)
                time.sleep(1)
                self._run_navis()
                return

        # If Navis window is not open, start Navis.
        else:
            self._run_navis()

            # Look 30s for Navis window to open
            navis_logo_found = pyautogui.locateOnScreen(
                image=NAVIS_LOGO,
                region=INITIAL_LOGO_REGION,
                minSearchTime=60) # Give Navis window time to load,
                # it can be PAINFULLY slow.
            
            if navis_logo_found:
                self._grab_navis_window()
                return
            else:
                raise Exception("Navis window not found.")

    def _run_navis(self) -> None:
        """Starts Navis program.
        Called by 'get_navis' function.

        Calls '_log_in_to_navis' function.
        """

        print("\nNavis window not found, starting program...")

        NAVIS_LOGIN_SCREEN = self.png['startup'].get('navis_login')
        NAVIS_REGION = tuple([int(i) for i in self.region.get('navis_login')])  #x, y, width, height

        navis = os.path.join(Path.home(), self.file.get('navis_jnlp'))
        os.startfile(navis)

        navis_login_screen_found = pyautogui.locateOnScreen(
            image=NAVIS_LOGIN_SCREEN,
            region=NAVIS_REGION,
            minSearchTime=20  # Give Navis login window time to load.
            )
        if navis_login_screen_found:
            self._log_in_to_navis()


    def _log_in_to_navis(self) -> None:
        """Logs in to Navis.
        Called by '_run_navis' function.
        """
        pyautogui.PAUSE = 0.1

        pyautogui.write(self.login.get('user'))
        pyautogui.press('tab')
        pyautogui.write(self.login.get('password'))
        pyautogui.press('enter')

        pyautogui.PAUSE = self.config['gui'].get('pause')
        

    def voyage_exist(self, value: str) -> tuple:
        """Checks if voyage exist in Navis.
        
        :param value: voyage number.
        """

        VOYAGE_TAB = self.coordinate.get('voyage_tab')
        VOYAGE_FIELD = self.coordinate.get('voyage_field')
        VOYAGE_REGION = tuple([int(i) for i in self.region.get('voyage')])  #x, y, width, height
        ACTIVE_VESSEL = self.png['booking'].get('active_vessel')

        pyautogui.click(VOYAGE_TAB, duration=0.5)
        time.sleep(1)
        pyautogui.click(VOYAGE_FIELD, duration=0.5)
        time.sleep(1)
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
        pyautogui.press('backspace')
        pyautogui.write(str(value))
        pyautogui.press('enter')
        time.sleep(5)  # Give Navis time to update,
        # may find image for wrong voyage otherwise.

        coordinate_exist = pyautogui.locateOnScreen(
            image=ACTIVE_VESSEL,
            region= VOYAGE_REGION,
            minSearchTime=1
            )
        return coordinate_exist


    def booking_exist(self, value: str) -> tuple:
        """Checks if booking exist in Navis.
        
        :param value: booking number.
        """

        BOOKING_TAB = self.coordinate.get('booking_tab')
        BOOKING_FIELD = self.coordinate.get('booking_field')
        BOOKING_REGION = tuple([int(i) for i in self.region.get('booking')])  #x, y, width, height
        BOOKING_EXIST = self.png['booking'].get('booking_exist')

        pyautogui.click(BOOKING_TAB, duration=0.5)
        time.sleep(1)
        pyautogui.click(BOOKING_FIELD, duration=0.5)
        time.sleep(1)
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
        pyautogui.press('backspace')
        pyautogui.write(str(value))
        pyautogui.press('enter')

        time.sleep(2)
        
        coordinate_exist = pyautogui.locateOnScreen(
            image=BOOKING_EXIST,
            region=BOOKING_REGION,
            minSearchTime=1
            )
        return coordinate_exist

    def add_booking(self, data: dict) -> None:
        """Adds booking to Navis.
        
        :param data: dictionary with booking data.
        """

        # [Booking scope] Presses 'Save' to save booking.
        pyautogui.leftClick(self.coordinate.get('add_booking'), duration=0.5)
        time.sleep(3)

        pyautogui.write(data['booking_no'])
        pyautogui.press('tab')
        time.sleep(1)

        pyautogui.write('EGL')
        time.sleep(3)
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

        # [Booking scope] Presses 'Save' to save booking.
        pyautogui.leftClick(
            self.coordinate.get('save_booking'),
            duration=0.5
            )
        time.sleep(3)

        # [amount of units, sequence no, weight per unit (kg)].
        unit_dict = {
            '45G1': [data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
            '42G1': [data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
            '22G1': [data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]
            }
        
        for value in unit_dict.values():
            if value[0] == 0:
                continue
            
            # [Unit scope] Presses 'Add' -> 'Add Booking Item'.
            pyautogui.leftClick(
                self.coordinate.get('add_equipment'),
                duration=0.5
                )
            time.sleep(4)
            
            pyautogui.write(str(value[0]))
            pyautogui.press('tab')

            pyautogui.write(str(value[1]))
            pyautogui.press('tab')

            pyautogui.write(str(value[2]))
            pyautogui.press('tab')

            # [Unit scope] locates equ_weight, left clicks box and writes weight
            weight_coord = pyautogui.locateOnScreen(
                image=self.png['equipment'].get('equ_weight'),
                minSearchTime=3
                )
            pyautogui.leftClick(
                weight_coord[0] + 200,
                weight_coord[1] + 4,
                duration=0.5
                )
            pyautogui.write(str(value[3]))

            # If there is hazardous information
            if value[4]:
                self.add_hazards_info(value[4])

            # [Unit scope] Presses 'Save' to save unit and then 'Close'
            pyautogui.leftClick(
                self.coordinate.get('save_equipment'),
                duration=0.5)
            time.sleep(3)
            pyautogui.move(xOffset=45, yOffset=0, duration=0.2)
            pyautogui.leftClick()
            time.sleep(3)


    def force_update_booking(self, data: dict) -> None:
        """Forces update of booking in Navis.
        
        :param data: dictionary with booking data.
        """

        time.sleep(5)
        # Click vessel visit field
        pyautogui.leftClick(
            self.coordinate.get('vessel_visit'),
            duration=0.5
            )
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
        pyautogui.press('backspace')
        pyautogui.write(str(data['navis_voy']))
        pyautogui.press('tab')
        time.sleep(2)

        # Clicks 'TOD' field
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


    def click_edit_booking(self, coordinates: pyautogui.Point):
        """Clicks 'Edit Booking' on booking in Navis.
        
        :param coordinates: tuple with coordinates of booking.
        """
        
        pyautogui.rightClick(coordinates, duration=0.5)
        pyautogui.move(xOffset=10, yOffset=10)
        pyautogui.leftClick(duration=0.5)
        time.sleep(6)


    def close_booking_window(self):
        """Closes booking window in Navis."""

        # Press 'Close' on [Booking scope]
        pyautogui.leftClick(
            self.coordinate.get('close_booking'),
            duration=0.5
            )


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

        ERROR_IMAGE = self.png['error_handling'].get('delete_units_gated_in')
        ERROR_REGION = tuple([int(i) for i in self.region.get('error_units_gated_in')])
        
        coord = pyautogui.locateOnScreen(
            image=ERROR_IMAGE,
            minSearchTime=2,
            region=ERROR_REGION
            )
        if coord:
            pyautogui.leftClick(
                self.coordinate.get('error_message_click_ok'),
                duration=0.5
                )


    def check_and_handle_equ_update_error(self):
        """Checks for error message and handles it if found."""

        ERROR_IMAGE = self.png['error_handling'].get('update_less_than_gated_in')
        ERROR_REGION = tuple([int(i) for i in self.region.get('error_update_less_than_gated_in')])
        
        coord = pyautogui.locateOnScreen(
            image=ERROR_IMAGE,
            minSearchTime=2,
            region=ERROR_REGION
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
        EQUIPMENT_SEARCH = tuple([int(i) for i in self.region.get('equipment_search')])
        IMAGE_40HC = self.png['equipment'].get('40hc')
        IMAGE_40DV = self.png['equipment'].get('40dv')
        IMAGE_20DV = self.png['equipment'].get('20dv')
        EQU_WEIGHT = self.png['equipment'].get('equ_weight')

        # [boolean, image, amount of units, sequence no, equ type, weight per unit (kg), hazard].
        unit_dict = {
            '45G1': [bool_dict['count_40hc'], IMAGE_40HC, data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
            '42G1': [bool_dict['count_40dv'], IMAGE_40DV, data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
            '22G1': [bool_dict['count_20dv'], IMAGE_20DV, data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]
            }
        
        for unit in unit_dict.values():
            if unit[0]:  # If changes to unit type
                coord = pyautogui.locateOnScreen(
                    image=unit[1],
                    minSearchTime=3,
                    region=EQUIPMENT_SEARCH
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
                        image=EQU_WEIGHT,
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
