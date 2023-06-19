import pyautogui
import time
from eglhandler.src.navis.image_identifier import get_mouse_coords
import sys

db_dict = {
    'booking_no': '599999999999',
    'navis_voy': '326-2326',
    'tod': 'DECTB',
}

sleep_vessel_visit = 5
sleep_tod = 4

add_booking_button = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\add-booking.png"
vessel_visit_booking_window = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\vessel-visit-booking-window.png"
vessel_visit_box = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\vessel-visit-box.png"
save_booking = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\save-window.png"
line_operator_box = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\line-operator-box.png"
tod_box = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\port-of-discharge-box.png"
shipper_field = r"C:\Users\SWV224\Global Freight Solutions AB\XPF - Operations\Development\Python\egl-booking-handler\app\eglhandler\png\booking\shipper-field.png"

def add_booking(data: dict) -> None:
        """Adds booking to Navis.
        
        :param data: dictionary with booking data.
        """

        # Searches for add booking button, click it if found
        add_booking_found = get_mouse_coords(add_booking_button, duration=5)        
        if add_booking_found is None:
            print("Add booking button not found in Navis.")

            sys.exit()
        
        pyautogui.leftClick(add_booking_found, duration=0.5)

        # Searches for booking window, write booking number if found
        booking_window_found = get_mouse_coords(vessel_visit_booking_window, duration=50)
        if booking_window_found is None:
            print("Booking window not found in Navis.")
            sys.exit()

        time.sleep(0.5)
        pyautogui.write(data['booking_no'])
        time.sleep(0.5)
        pyautogui.press('tab')

        while True:
            pyautogui.write('EGL')
            line_operator_found = get_mouse_coords(line_operator_box, duration=0.5)

            if line_operator_found:
                break

        time.sleep(1)
        pyautogui.press('tab')

        while True:
            pyautogui.write(data['navis_voy'])
            vessel_visit_found = get_mouse_coords(vessel_visit_box, duration=0.5)
            
            if vessel_visit_found:
                break
               
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(2)
        pyautogui.press('tab')

        while True:        
            pyautogui.write(data['tod'])
            tod_found = get_mouse_coords(tod_box, duration=0.5)

            if tod_found:
                break

        time.sleep(1)
        pyautogui.press('tab')

        shipper_field_found = get_mouse_coords(shipper_field, duration=5)
        if shipper_field_found is None:
            print("Shipper field not found in Navis.")
            sys.exit()
        
        pyautogui.leftClick(shipper_field_found, duration=0.5)
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
        pyautogui.write('XCL')
        pyautogui.press('tab')

        save_booking_found = get_mouse_coords(save_booking, duration=5)
        if save_booking_found is None:
            print("Save booking button not found in Navis.")
            sys.exit()

        pyautogui.leftClick(save_booking_found, duration=0.5)
        time.sleep(1)

add_booking(db_dict)

"""        

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
            
            time.sleep(3)
            pyautogui.write(str(value[0]))
            time.sleep(1)
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.write(str(value[1]))
            time.sleep(1)
            pyautogui.press('tab')
            time.sleep(0.5)
            pyautogui.write(str(value[2]))
            time.sleep(2)
            pyautogui.press('tab')
            time.sleep(0.3)

            # Search for weight box, click it and write out weight
            equ_weight_found = get_mouse_coords(self.config.equ_weight, duration=5)
            if equ_weight_found is None:
                print("Weight box not found in Navis.")
                print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                sys.exit()

            time.sleep(1)
            pyautogui.leftClick(
                equ_weight_found[0] + 250,
                equ_weight_found[1],
                duration=0.3
                )
            pyautogui.write(str(value[3]))

            time.sleep(1)

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
"""