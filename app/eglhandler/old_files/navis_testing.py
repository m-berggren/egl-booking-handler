string1 = """navis_logo: str
    navis_logo_region: list
    navis_login: str
    navis_login_region: list
    connection_error: str
    error_gated_in: str
    error_gated_in_region: list
    error_less_than_gated_in: str
    error_less_than_gated_in_region: list
    voyage_tab: str
    voyage_tab_selected: str
    bookings_tab: str
    bookings_tab_selected: str
    vessels_and_booking_region: list
    voyage_field: str
    voyage_region: list
    booking_field: str
    booking_field_region: list
    vessel_exist: str
    vessel_exist_region: list
    booking_exist: str
    booking_exist_region: list
    add_booking: str
    add_booking_region: list
    booking_window: str
    booking_window_region: list
    save_booking: str
    save_booking_region: list
    image_40hc: str
    image_40dv: str
    image_20dv: str
    equipment_search_region: list
    add_equipment: str
    add_equipment_region: list
    equ_window: str
    equ_window_region: list
    save_equipment: str
    close_equipment: str
    save_equipment_region: list
    equ_weight: str
    equ_weight_region: list
    hazards_button: str
    hazards_region: list
    line_operator_box: str
    vessel_visit_box: str
    line_vessel_pod_boxes: list
    port_of_discharge_box: str
    hazards_button_add: str
    hazards_button_add_unno: str
    hazards_window_check: str
    hazards_save_button: str
    delete_booking: str
    equ_cancel_button: str
    equ_confirm_cancel: str
    vessel_visit_booking_window: str
    tod_booking_window: str"""

l1 = string1.split("\n")
l2 = [i.split(":")[0].strip() for i in l1]
len_l2 = len(l2)

string2 = """'navis_logo': navis.png.startup.navis_logo,
        'navis_login': navis.png.startup.navis_login,
        'navis_logo_region': navis.region.login.navis_logo,
        'navis_login_region': navis.region.login.navis_login,
        'connection_error': navis.png.error_handling.connection_error,
        'error_gated_in': navis.png.error_handling.delete_units_gated_in,
        'error_gated_in_region': navis.region.error.units_gated_in,
        'error_less_than_gated_in': navis.png.error_handling.update_less_than_gated_in,
        'error_less_than_gated_in_region': navis.region.error.update_less_than_gated_in,
        'voyage_tab': navis.png.booking.vessels_active,
        'voyage_tab_selected': navis.png.booking.vessels_active_selected,
        'bookings_tab': navis.png.booking.export,
        'bookings_tab_selected': navis.png.booking.export_selected,
        'vessels_and_booking_region': navis.region.exist.vessels_and_bookings,
        'voyage_field': navis.png.booking.vessels_active_field,
        'voyage_region': navis.region.exist.vessels_field,
        'booking_field': navis.png.booking.export_field,
        'booking_field_region': navis.region.exist.booking_field,
        'vessel_exist': navis.png.booking.active_vessel,
        'vessel_exist_region': navis.region.exist.vessel,
        'booking_exist': navis.png.booking.exist,
        'booking_exist_region': navis.region.exist.booking,
        'add_booking': navis.png.booking.add,
        'add_booking_region': navis.region.booking.add_button,
        'booking_window_region': navis.region.booking.validate_window,
        'save_booking': navis.png.booking.save_window,
        'save_booking_region': navis.region.booking.save_or_close,
        'image_40hc': navis.png.equipment.hc40,
        'image_40dv': navis.png.equipment.dv40,
        'image_20dv': navis.png.equipment.dv20,
        'equipment_search_region': navis.region.booking.equipment_search,
        'add_equipment': navis.png.booking.add_equ,
        'add_equipment_region': navis.region.equipment.add_button,
        'equ_window': navis.png.equipment.equ_window_check,
        'equ_window_region': navis.region.equipment.validate_window,
        'save_equipment': navis.png.booking.save_window,
        'close_equipment': navis.png.booking.close_window,
        'save_equipment_region': navis.region.equipment.save,
        'equ_weight': navis.png.equipment.equ_weight,
        'equ_weight_region': navis.region.equipment.unit_weight,
        'hazards_button': navis.png.equipment.hazards_button,
        'hazards_region': navis.region.equipment.hazards_region,
        'line_operator_box': navis.png.booking.line_operator_box,
        'vessel_visit_box': navis.png.booking.vessel_visit_box,
        'line_vessel_pod_boxes': navis.region.booking.line_vessel_pod_boxes,
        'port_of_discharge_box': navis.png.booking.port_of_discharge_box,
        'hazards_button_add': navis.png.equipment.hazards_button_add,
        'hazards_button_add_unno': navis.png.equipment.hazards_button_add_unno,
        'hazards_window_check': navis.png.equipment.hazards_window_check,
        'hazards_save_button': navis.png.equipment.hazards_save_button,
        'delete_booking': navis.png.booking.delete_booking,
        'equ_cancel_button': navis.png.equipment.equ_cancel_button,
        'equ_confirm_cancel': navis.png.equipment.equ_confirm_cancel,
        'vessel_visit_booking_window': navis.png.booking.vessel_visit_booking_window,
        'tod_booking_window': navis.png.booking.tod_booking_window,"""

l3 = string2.split("\n")
l4 = [i.split(":")[0].strip() for i in l3]
l4 = [i.replace("'", "") for i in l4]


def find_missing_value(list1, list2):
    if len(list1) == len(list2):
        return None  # Lists have the same length, no missing values
    
    shorter_list = list1 if len(list1) < len(list2) else list2
    longer_list = list2 if shorter_list is list1 else list1
    
    missing_value = None
    
    for value in longer_list:
        if value not in shorter_list:
            missing_value = value
            break
    
    return missing_value

missing = find_missing_value(l2, l4)

if missing is not None:
    print(f"Missing value: {missing}")
else:
    print("No missing value found")

""""""
"""
def write_and_find_vessel_visit_box(duration: float) -> None:
            
            start_time = time.time()
            while True:
                pyautogui.write(data['navis_voy'])
                time.sleep(0.3)
                vessel_visit_box_found = get_mouse_coords(
                    self.config.vessel_visit_box,
                    region=self.config.line_vessel_pod_boxes,
                    duration=0.3
                    )
                if vessel_visit_box_found:
                    break

                elapsed_time = time.time() - start_time
                if elapsed_time >= duration:
                    print("Vessel visit box not found in Navis Booking window.")
                    print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
                    sys.exit()"""

"""
            port_of_discharge_box_found = get_mouse_coords(
            self.config.port_of_discharge_box,
            region=self.config.line_vessel_pod_boxes,
            duration=3

            if port_of_discharge_box_found is None:
            print("Port of discharge box not found in Navis Booking window.")
            print(f"Class: {self.__class__.__name__}, Function: {inspect.stack()[0].function}")
            sys.exit()
        )"""