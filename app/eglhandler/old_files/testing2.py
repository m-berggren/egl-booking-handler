import re

s = """navis_logo: navis.png.startup.navis_logo
    navis_login: navis.png.startup.navis_login
    navis_logo_region: navis.region.login.navis_logo
    navis_login_region: navis.region.login.navis_login
    connection_error: navis.png.error_handling.connection_error
    error_gated_in: navis.png.error_handling.delete_units_gated_in
    error_gated_in_region: navis.region.error.units_gated_in
    error_less_than_gated_in: navis.png.error_handling.update_less_than_gated_in
    error_less_than_gated_in_region: navis.region.error.update_less_than_gated_in
    voyage_tab: navis.png.booking.vessels_active
    voyage_tab_selected: navis.png.booking.vessels_active_selected
    bookings_tab: navis.png.booking.export
    bookings_tab_selected: navis.png.booking.export_selected
    vessels_and_booking_region: navis.region.exist.vessels_and_bookings
    voyage_field: navis.png.booking.vessels_active_field
    voyage_region: navis.region.exist.vessels_field
    booking_field: navis.png.booking.export_field
    booking_field_region: navis.region.exist.booking_field
    vessel_exist: navis.png.booking.active_vessel
    vessel_exist_region: navis.region.exist.vessel
    booking_exist: navis.png.booking.exist
    booking_exist_region: navis.region.exist.booking
    add_booking: navis.png.booking.add
    add_booking_region: navis.region.booking.add_button
    booking_window: navis.png.booking.add_or_edit
    booking_window_region: navis.region.booking.validate_window
    save_booking: navis.png.booking.save_window
    save_booking_region: navis.region.booking.save_or_close
    image_40hc: navis.png.equipment.hc40
    image_40dv: navis.png.equipment.dv40
    image_20dv: navis.png.equipment.dv20
    equipment_search_region: navis.region.booking.equipment_search
    add_equipment: navis.png.booking.add_equ
    add_equipment_region: navis.region.equipment.add_button
    equ_window: navis.png.booking.equ_window_check
    equ_window_region: navis.region.equipment.validate_window
    save_equipment: navis.png.booking.save_window
    close_equipment: navis.png.booking.close_window
    save_equipment_region: navis.region.equipment.save
    equ_weight: navis.png.equipment.equ_weight
    equ_weight_region: navis.region.equipment.unit_weight"""

t = """- navis_logo
    - navis_login
    - navis_logo_region
    - navis_login_region
    - connection_error
    - error_gated_in
    - error_gated_in_region
    - error_less_than_gated_in
    - error_less_than_gated_in_region
    - voyage_tab
    - voyage_tab_selected
    - bookings_tab
    - bookings_tab_selected
    - vessels_and_booking_region
    - voyage_field
    - voyage_region
    - booking_field
    - booking_field_region
    - vessel_exist
    - vessel_exist_region
    - booking_exist
    - booking_exist_region
    - add_booking
    - add_booking_region
    - booking_window
    - booking_window_region
    - save_booking
    - save_booking_region
    - image_40hc
    - image_40dv
    - image_20dv
    - equipment_search_region
    - add_equipment
    - add_equipment_region
    - equ_window
    - equ_window_region
    - save_equipment
    - close_equipment
    - save_equipment_region
    - equ_weight
    - equ_weight_region"""
string = s.split("\n")

l1 = {}

for i in string:
    stripped = i.strip()
    matching = re.match(r"(.+):\s(.+)$", stripped)
    
    if matching:
        key = matching.group(1)
        value = matching.group(2)
        l1[key] = value


for i in string:
    matching = re.match(r"^.+:", i)
    if matching:
        print(f"    - {matching.group(0)[:-1]}")






