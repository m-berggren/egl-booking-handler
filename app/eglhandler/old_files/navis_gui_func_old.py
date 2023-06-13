import time

import pyautogui
import win32gui




# Sets the overall delay between every PyAutoGUI call.
pyautogui.PAUSE = 2

# Sets a failsafe for PyAutoGUI. If the mouse cursor is in the upper left corner
pyautogui.FAILSAFE = True

def grab_navis_window():
        def windowEnumerationHandler(hwnd, top_windows):
            top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
        top_windows = []
        win32gui.EnumWindows(windowEnumerationHandler, top_windows)
        for window in top_windows:
            if "navis n4" in window[1].lower():
                # Pressing 'alt' appears to make the program more stable.
                pyautogui.press("alt")
                win32gui.ShowWindow(window[0],5)
                win32gui.ShowWindow(window[0],9)
                win32gui.SetForegroundWindow(window[0])
                return True
        return False


def get_navis_logo():
    NAVIS_LOGO = r"egl_booking_handler\png\navis_logo.png"
    LOGO_REGION = (1540, 870, 140, 50)  #x, y, width, height

    if grab_navis_window():
        navis_logo = pyautogui.locateOnScreen(image=NAVIS_LOGO, region=LOGO_REGION, minSearchTime=0.5)

        if navis_logo:
            return True
        else:
            return False
    else:
         return False
    

def voyage_exist(value: str) -> tuple:
    MENU_TAB = 400, 200
    SEARCH_FIELD = 1270, 228
    SEARCH_REGION = (300, 200, 500, 300)

    pyautogui.click(MENU_TAB, duration=0.5)
    time.sleep(1)
    pyautogui.click(SEARCH_FIELD, duration=0.5)
    time.sleep(1)
    with pyautogui.hold('ctrl'):
        pyautogui.press('a')
    pyautogui.press('backspace')
    pyautogui.write(str(value))
    pyautogui.press('enter')
    time.sleep(3)  # Give Navis time to update, may find image for wrong voyage otherwise.

    coordinate_exist = pyautogui.locateOnScreen(
        image=r'egl_booking_handler\png\active_vessel\active_vessel_search_result.png',
        region=SEARCH_REGION,
        minSearchTime=4
        )
    return coordinate_exist


def booking_exist(value: str) -> tuple:
    MENU_TAB = 650, 200
    SEARCH_FIELD = 1150, 228
    SEARCH_REGION = (1200, 260, 1300, 290)
    
    pyautogui.click(MENU_TAB, duration=0.5)
    time.sleep(1)
    pyautogui.click(SEARCH_FIELD, duration=0.5)
    time.sleep(1)
    with pyautogui.hold('ctrl'):
        pyautogui.press('a')
    pyautogui.press('backspace')
    pyautogui.write(str(value))
    pyautogui.press('enter')

    time.sleep(2)
    
    coordinate_exist = pyautogui.locateOnScreen(
        image=r'egl_booking_handler\png\booking_exist\booking_exist.png',
        region=SEARCH_REGION,
        minSearchTime=1
        )
    return coordinate_exist

def add_booking(data: dict) -> None:

    # [Booking scope] Presses 'Save' to save booking.
    pyautogui.leftClick(x=1630, y=229, duration=0.5)
    time.sleep(3)

    pyautogui.write(data['booking_no'])
    pyautogui.press('tab')
    time.sleep(1)

    pyautogui.write('EGL')
    time.sleep(3)
    pyautogui.press('tab')
    time.sleep(5)

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
    pyautogui.leftClick(x=1383, y=878, duration=0.5)
    time.sleep(3)

    # [amount of units, sequence no, weight per unit (kg)].
    unit_dict = {'45G1': [data['count_40hc'], 1, "45G1", data['weight_40hc']],
                 '42G1': [data['count_40dv'], 2, "42G1", data['weight_40dv']],
                 '22G1': [data['count_20dv'], 3, "22G1", data['weight_20dv']]}
    
    for value in unit_dict.values():
        if value[0] == 0:
            continue
        
        # [Unit scope] Presses 'Add' -> 'Add Booking Item'.
        pyautogui.leftClick(x=1423, y=619, duration=0.5)
        time.sleep(4)
        
        pyautogui.write(str(value[0]))
        pyautogui.press('tab')

        pyautogui.write(str(value[1]))
        pyautogui.press('tab')

        pyautogui.write(str(value[2]))
        pyautogui.press('tab')

        weight_coord = pyautogui.locateOnScreen(image=r'egl_booking_handler\png\booking_create\equ_weight.png',
                                                minSearchTime=3)
        pyautogui.leftClick(weight_coord[0] + 200, weight_coord[1] + 4, duration=0.5)
        pyautogui.write(str(value[3]))

        # [Unit scope] Presses 'Save' to save unit and then 'Close'.
        pyautogui.leftClick(x=1248, y=880, duration=0.5)
        time.sleep(3)
        pyautogui.move(xOffset=45, yOffset=0, duration=0.2)
        pyautogui.leftClick()
        time.sleep(3)


def force_update_booking(data: dict) -> None:
    time.sleep(5)
    # Find vessel voyage.
    pyautogui.leftClick(x=642, y=248, duration=0.5)
    with pyautogui.hold('ctrl'):
        pyautogui.press('a')
    pyautogui.press('backspace')
    pyautogui.write(str(data['navis_voy']))
    pyautogui.press('tab')
    time.sleep(2)

    # Finds tod.
    pyautogui.leftClick(x=638, y=268, duration=0.5)
    with pyautogui.hold('ctrl'):
        pyautogui.press('a')
    pyautogui.press('backspace')
    pyautogui.write(str(data['tod']))
    pyautogui.press('tab')
    time.sleep(2)

    # TODO: Add hazard option.

    # [Booking scope] Presses 'Save' to save booking.
    pyautogui.leftClick(x=1383, y=878, duration=0.5)


def click_edit_booking(coordinates):
    pyautogui.rightClick(coordinates, duration=0.5)
    pyautogui.move(xOffset=10, yOffset=10)
    pyautogui.leftClick(duration=0.5)
    time.sleep(6)


def close_booking_window():
    # Press 'Close' on [Booking scope]
    pyautogui.leftClick(x=1423, y=877, duration=0.5)


def update_booking_info(data: dict, bool_dict: dict) -> None:
    time.sleep(4)
    if bool_dict['navis_voy']:
        # Finds vessel voyage.
        pyautogui.leftClick(x=642, y=248, duration=0.5)
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
        pyautogui.press('backspace')
        pyautogui.write(str(data['navis_voy']))
        pyautogui.press('tab')
        time.sleep(2)

    if bool_dict['tod']:
        # Finds tod.
        pyautogui.leftClick(x=638, y=268, duration=0.5)
        with pyautogui.hold('ctrl'):
            pyautogui.press('a')
        pyautogui.press('backspace')
        pyautogui.write(str(data['tod']))
        pyautogui.press('tab')
        time.sleep(2)

    # [Booking scope] Presses 'Save' to save booking.
    pyautogui.leftClick(x=1383, y=878, duration=0.5)
    time.sleep(2)
    

def check_and_handle_delete_equ_error():
    SEARCH_REGION = (595, 372, 545, 141)
    ERROR_IMAGE = r"egl_booking_handler\png\equipment_edit\error_delete_units_gated_in.png"

    coord = pyautogui.locateOnScreen(image=ERROR_IMAGE,
                             minSearchTime=2,
                             region=SEARCH_REGION)
    if coord:
        pyautogui.leftClick(1235, 639, duration=0.5)


def check_and_handle_equ_update_error():
    SEARCH_REGION = (627, 395, 377, 107)
    ERROR_IMAGE = r"egl_booking_handler\png\equipment_edit\error_update_less_than_units_gated_in.png"

    coord = pyautogui.locateOnScreen(image=ERROR_IMAGE,
                                     minSearchTime=2,
                                     region=SEARCH_REGION)
    if coord:
        # Click 'OK' on error message.
        pyautogui.leftClick(1236, 638, duration=0.5)
        # Click 'Cancel' [Unit scope]
        pyautogui.leftClick(1304, 878, duration=0.5)
        # Confirm 'Yes'
        pyautogui.leftClick(921, 588, duration=0.5)


def confirm_delete_units():
    pyautogui.leftClick(919, 571, duration=0.5)


def update_equ_info(data: dict, bool_dict: dict) -> None:
    time.sleep(4)
    SEARCH_REGION = (750, 650, 76, 160)
    IMAGE_40HC = r'egl_booking_handler\png\equipment_edit\45G1.png'
    IMAGE_40DV = r'egl_booking_handler\png\equipment_edit\42G1.png'
    IMAGE_20DV = r'egl_booking_handler\png\equipment_edit\22G1.png'
    EQU_WEIGHT = r'egl_booking_handler\png\booking_create\equ_weight.png'

    # [amount of units, sequence no, weight per unit (kg)].
    unit_dict = {'45G1': [bool_dict['count_40hc'], IMAGE_40HC, data['count_40hc'], 1, "45G1", data['weight_40hc'], data['hazard_40hc']],
                '42G1': [bool_dict['count_40dv'], IMAGE_40DV, data['count_40dv'], 2, "42G1", data['weight_40dv'], data['hazard_40dv']],
                '22G1': [bool_dict['count_20dv'], IMAGE_20DV, data['count_20dv'], 3, "22G1", data['weight_20dv'], data['hazard_20dv']]}
    
    for unit in unit_dict.values():
        if unit[0]:  # If changes to unit type
            coord = pyautogui.locateOnScreen(image=unit[1],
                                    minSearchTime=3,
                                    region=SEARCH_REGION
                                    )
            pyautogui.rightClick(coord, duration=0.5)

            if unit[2] == 0:  # If data is 0 then delete row
                pyautogui.move(xOffset=42, yOffset=65, duration=0.5)
                pyautogui.leftClick()
                confirm_delete_units()
                check_and_handle_delete_equ_error()

            elif not coord:  # If image is not found
                # [Unit scope] Presses 'Add' -> 'Add Booking Item'.
                pyautogui.leftClick(x=1423, y=619, duration=0.5)
                time.sleep(4)

                pyautogui.write(str(unit[2]))
                pyautogui.press('tab')

                pyautogui.write(str(unit[3]))
                pyautogui.press('tab')

                pyautogui.write(str(unit[4]))
                pyautogui.press('tab')

                weight_coord = pyautogui.locateOnScreen(image=EQU_WEIGHT,
                                                        minSearchTime=3)
                pyautogui.leftClick(weight_coord[0] + 200, weight_coord[1] + 4, duration=0.5)
                pyautogui.write(str(unit[5]))

                # TODO: Add hazards option

                # [Unit scope] Presses 'Save' to save unit and then 'Close'.
                pyautogui.leftClick(x=1248, y=880, duration=0.5)
                time.sleep(3)
                pyautogui.move(xOffset=45, yOffset=0, duration=0.2)
                pyautogui.leftClick()
                time.sleep(3)

            else:
                pyautogui.move(xOffset=10, yOffset=10, duration=0.5)
                pyautogui.leftClick()
                time.sleep(4)

                pyautogui.write(str(unit[2]))
                pyautogui.press('tab')

                # [Unit scope] Presses 'Save' to save unit.
                pyautogui.leftClick(x=1248, y=880, duration=0.5)

                # Check for error message (when containers set are less than what is delivered).
                check_and_handle_equ_update_error()


def delete_booking(coordinates):
    time.sleep(3)   # Navis may need some extra time to refresh properly.
    pyautogui.rightClick(coordinates, duration=0.5)
    pyautogui.move(xOffset=24, yOffset=60, duration=0.5)
    pyautogui.leftClick()
    pyautogui.leftClick(x=920, y=570, duration=0.5)

    # Check for error message (when containers are collected or gated in).
    check_and_handle_delete_equ_error()


def add_hazards_info():
    # TODO: Add hazard info
    pass

if __name__ == '__main__':
    pass