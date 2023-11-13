import os

import fitz

import eglhandler.src.parser.parser_functions as pf
from eglhandler.src.parser.constants import *


def parse_pdf(file_path: str, config: dict) -> dict:
    """Main function for parsing pdfs."""

    with open(file_path) as f:
        doc = fitz.open(f)
    
    total_height = 0.0
    total_words = []
    list_count_40hc, list_count_40dv, list_count_20dv = [], [], []
    list_tare_40hc, list_tare_40dv, list_tare_20dv = [], [], []
    list_nwt_40hc, list_nwt_40dv, list_nwt_20dv = [], [], []
    list_hazards_40hc, list_hazards_40dv, list_hazards_20dv = [], [], []
    
    
    for page in doc:
        word_list = page.get_text('words')

        # Check if this is an Evergreen booking or not.
        if "EVERGREEN" in word_list[0][4]:
            # Means this is not an Evergreen booking.
            return None

        for word in word_list:
            """Add the height of the page to the y coordinates of the words."""
            total_words.append([word[0], word[1] + total_height, word[2], word[3] + total_height, word[4]])
        
        
        d20 = page.search_for(CONTAINER_20DV)
        d40 = page.search_for(CONTAINER_40DV)
        h40 = page.search_for(CONTAINER_40HC)
    
        """Check if the page contains any of the container types, weights, information and hazards."""
        list_count_40hc.append(pf.get_container_amount(total_words, h40, RECT_CONTAINER_HC, total_height))
        list_count_40dv.append(pf.get_container_amount(total_words, d40, RECT_CONTAINER_DV, total_height))
        list_count_20dv.append(pf.get_container_amount(total_words, d20, RECT_CONTAINER_DV, total_height))

        list_nwt_40hc.append(pf.get_container_info(total_words, h40, RECT_CONTAINER_WEIGHTS, total_height)[0])
        list_nwt_40dv.append(pf.get_container_info(total_words, d40, RECT_CONTAINER_WEIGHTS, total_height)[0])
        list_nwt_20dv.append(pf.get_container_info(total_words, d20, RECT_CONTAINER_WEIGHTS, total_height)[0])
    
        list_tare_40hc.append(pf.get_container_info(total_words, h40, RECT_CONTAINER_WEIGHTS, total_height)[1])
        list_tare_40dv.append(pf.get_container_info(total_words, d40, RECT_CONTAINER_WEIGHTS, total_height)[1])
        list_tare_20dv.append(pf.get_container_info(total_words, d20, RECT_CONTAINER_WEIGHTS, total_height)[1])

        list_hazards_40hc.append(pf.get_container_hazards(total_words, h40, RECT_HAZARDS, total_height))
        list_hazards_40dv.append(pf.get_container_hazards(total_words, d40, RECT_HAZARDS, total_height))
        list_hazards_20dv.append(pf.get_container_hazards(total_words, d20, RECT_HAZARDS, total_height))

        total_height += page.rect.height
    
    
    booking_revised = pf.get_value_in_rect(doc, total_words, BOOKING_REVISED, RECT_BOOKING_REVISED)
    date_booked = pf.get_value_in_rect(doc, total_words, DATE_BOOKED, RECT_DATE_BOOKED)
    booking_number = pf.get_value_in_rect(doc, total_words, BOOKING_NUMBER, RECT_BOOKING_NUMBER)
    departure_voy = pf.get_value_in_rect(doc, total_words, DEPARTURE_WEEK, RECT_DEPARTURE_WEEK)
    port_of_loading = pf.get_value_in_rect(doc, total_words, PORT_OF_LOADING, RECT_PORT_OF_LOADING)
    departure_date = pf.get_value_in_rect(doc, total_words, DEPARTURE_DATE, RECT_DEPARTURE_DATE)
    discharge_port = pf.get_value_in_rect(doc, total_words, DISCHARGE_PORT, RECT_DISCHARGE_PORT)
    mother_vessel = pf.get_value_in_rect(doc, total_words, MOTHER_VESSEL, RECT_MOTHER_VESSEL)
    stowage_code = pf.get_value_in_rect(doc, total_words, STOWAGE_CODE, RECT_STOWAGE_CODE)
    final_pod = pf.get_value_in_rect(doc, total_words, FINAL_POD, RECT_FINAL_POD)
    commodity = pf.get_value_in_rect(doc, total_words, COMMODITY, RECT_COMMODITY)
    discharge_terminal = pf.get_value_in_rect(doc, total_words, DISCHARGE_TERMINAL, RECT_DISCHARGE_TERMINAL)

    trimmed_booked_date = pf.trim_date_string(date_booked)
    terminal = pf.map_from_dict_terminal(config, discharge_terminal, stowage_code, section='tod')
    vessel = pf.map_from_dict(config, terminal, section='vessel')
    week = pf.departure_week(departure_date)
    navis_voyage = pf.navis_voyage(terminal, vessel, departure_date, week)

    # Sometimes bookings are sent to us where POL is not Gothenburg. These bookings are not relevant to us.
    if "GOTHENBURG" not in port_of_loading:
        return None
    
    # Return a dictionary with all the information we need.
    return_dict = {
        'booking_revised': pf.check_revised_status(booking_revised)[0],
        'cancellation' : pf.check_revised_status(booking_revised)[1],
        'booking_number': booking_number,
        'port_of_loading': port_of_loading,
        'date_booked': trimmed_booked_date,
        'same_date': pf.check_if_dates_match(trimmed_booked_date, departure_date),
        'departure_voy': departure_voy,
        'departure_week': week,
        'navis_voy': navis_voyage,
        'departure_date': departure_date,
        'discharge_port': pf.map_from_dict(config, discharge_port, section='pod'),
        'ocean_vessel': pf.ocean_vessel_and_voy(mother_vessel)['vessel'],
        'voyage': pf.ocean_vessel_and_voy(mother_vessel)['voy'],
        'stowage_code': stowage_code,
        'final_pod': pf.extract_final_pod(final_pod),
        'commodity': commodity,
        'discharge_terminal': terminal,
        'container_amount': {'45G1': pf.concatenate_floats(list_count_40hc),
                             '42G1': pf.concatenate_floats(list_count_40dv),
                             '22G1': pf.concatenate_floats(list_count_20dv)
                            },
        'weights': {'45G1': pf.calculate_vgm(list_nwt_40hc, list_tare_40hc, list_count_40hc),
                    '42G1': pf.calculate_vgm(list_nwt_40dv, list_tare_40dv, list_count_40dv),
                    '22G1': pf.calculate_vgm(list_nwt_20dv, list_tare_20dv, list_count_20dv)
                    },        
        'hazardous_cargo': {'45G1': pf.create_string_of_unnos(list_hazards_40hc),
                            '42G1': pf.create_string_of_unnos(list_hazards_40dv),
                            '22G1': pf.create_string_of_unnos(list_hazards_20dv)
                            },
        'booking_in_navis': 1  #1 means True, value will change at a later stage if booking is not sucessfully imported to Navis.
    }
    return return_dict


def booking_info(dir: str, pdf_file: str, config: dict) -> tuple:
    """ Function that takes a directory and a pdf file and returns a dictionary with booking information."""

    if pdf_file is None:
        return None, None, None, None

    # Get all data from pdf
    pdf_data = parse_pdf(os.path.join(dir, pdf_file), config)

    # If file does not exist return None
    if pdf_data is None:
        data = None
        same_date = None
        cancellation = None
        terminal = None
        return data, same_date, cancellation, terminal

    # Creates dictionary with information from pdf_data
    data ={
        'cancellation': pdf_data['cancellation'],
        'revised_no': pdf_data['booking_revised'],
        'booking_no': pdf_data['booking_number'],
        'booking_in_navis': pdf_data['booking_in_navis'],
        'date_booked': pdf_data['date_booked'],
        'etd': pdf_data['departure_date'],
        'navis_voy': pdf_data['navis_voy'],
        'pod': pdf_data['discharge_port'],
        'tod': pdf_data['discharge_terminal'],
        'ocean_vessel': pdf_data['ocean_vessel'],
        'voyage': pdf_data['voyage'],
        'final_dest': pdf_data['final_pod'],
        'commodity': pdf_data['commodity'],
        'count_40hc': pdf_data['container_amount']['45G1'],
        'count_40dv': pdf_data['container_amount']['42G1'],
        'count_20dv': pdf_data['container_amount']['22G1'],
        'weight_40hc': pdf_data['weights']['45G1'],
        'weight_40dv': pdf_data['weights']['42G1'],
        'weight_20dv': pdf_data['weights']['22G1'],
        'hazard_40hc': pdf_data['hazardous_cargo']['45G1'],
        'hazard_40dv': pdf_data['hazardous_cargo']['42G1'],
        'hazard_20dv': pdf_data['hazardous_cargo']['22G1'],
        'pdf_name': pdf_file
        
    }
    # Three additional values added separately
    same_date = pdf_data['same_date']
    cancellation = pdf_data['cancellation']
    terminal = pdf_data['discharge_terminal']

    return data, same_date, cancellation, terminal


if __name__ == '__main__':
    
    def parse_one_file(file, config):
        print(parse_pdf(file, config))
        
    import yaml
    with open(r"..\app\eglhandler\config.yaml", 'r') as _f:
        config = yaml.safe_load(_f)
    
    directory = config['directories'].get('parsed')
    file = os.path.join('..', directory, r"SBB6S0P2.PDF")
    #file = os.path.join('..', directory, r"SBB0T6YQ.PDF")
    parse_one_file(file, config)




    
