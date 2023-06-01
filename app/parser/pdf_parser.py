import os

import fitz

import parser_functions as pf
from variables import *


def main(file_path):

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

        if "EVERGREEN" in word_list[0][4]:
            # Means this is not an Evergreen booking.
            return None

        for word in word_list:
            total_words.append([word[0], word[1] + total_height, word[2], word[3] + total_height, word[4]])
    
        d20 = page.search_for(CONTAINER_20DV)
        d40 = page.search_for(CONTAINER_40DV)
        h40 = page.search_for(CONTAINER_40HC)
    
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
    terminal = pf.map_from_dict(CONFIG_FILE, discharge_terminal, stowage_code, section=3)
    vessel = pf.map_from_dict(CONFIG_FILE, terminal, section=1)
    week = pf.departure_week(departure_date)
    navis_voyage = pf.navis_voyage(terminal, vessel, departure_date, week)

    if "GOTHENBURG" not in port_of_loading:
        return None

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
        'discharge_port': pf.map_from_dict(CONFIG_FILE, discharge_port, section=2),
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
        'hazardous_cargo': {'45G1': pf.create_hazards_list(list_hazards_40hc),
                            '42G1': pf.create_hazards_list(list_hazards_40dv),
                            '22G1': pf.create_hazards_list(list_hazards_20dv)
                            },
        'booking_in_navis': True
    }
    return return_dict

def booking_info(dir, pdf_file):

    # Get all data from pdf
    pdf_data = main(os.path.join(dir, pdf_file))

    # If file does not exist return None
    if pdf_data is None:
        data = None
        same_date = None
        cancellation = None
        terminal = None
        return data, same_date, cancellation, terminal

    # Creates dictionary with information from pdf_data
    data ={
        'revised_no': pdf_data['booking_revised'],
        'booking_no': pdf_data['booking_number'],
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
        'booking_in_navis': pdf_data['booking_in_navis'],
        'pdf_name': pdf_file
        
    }
    # Two additional values added separately
    same_date = pdf_data['same_date']
    cancellation = pdf_data['cancellation']
    terminal = pdf_data['discharge_terminal']

    return data, same_date, cancellation, terminal


if __name__ == '__main__':

    ROOT_DIR = os.path.abspath('')
    pdf_folder = r".\docs\downloaded_pdfs"
    file_dir = os.path.join(ROOT_DIR, pdf_folder)

    with open('tests\pdf_parser_test.txt', 'w') as f:
        for file in os.listdir(pdf_folder):
            nl = "\n"
            break_line = "|" + "------------------------"*3 + "|"+ nl
            f.write(break_line)
            print(break_line)
            main_info = main(os.path.join(pdf_folder, file))
            if main_info is not None:
                for key, value in main_info.items():
                    string = f'|{key:>20}: {str(value):<50}|'
                    f.write(string + nl)
                    print(string)



    
