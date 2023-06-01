import configparser
import itertools
import re
from datetime import datetime

import fitz

"""
Functions for pdf_parser file.
"""

def get_value_in_rect(doc, total_words, search_str, rect_add=(0, 0, 0, 0)):
    try:
        rect = doc[0].search_for(search_str)[0] + rect_add
    except IndexError:
        return ""

    if rect:
        try:
            return re.match(r'^:*(.*)',' '.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)])).group(1)
        except IndexError:
            return ""

    
def get_container_amount(total_words, rect_list, rect_add, height):
    list_count = []
    for rect in rect_list:
        rect = rect + rect_add + (0, height, 0, height)
        result = re.sub(r'^\+*', '',''.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)])).replace(',', '')
        list_count.append(float(result))
    return list_count

def  check_revised_status(revised):
    cancelled = ""

    if revised == "CANCELLATION":
        cancelled = revised
        revised = 0

    return revised, cancelled
    
def get_container_info(total_words, rect_list, rect_add, height):
    list_count_nwt = []
    list_count_tare = []
    for rect in rect_list:
        rect = rect + rect_add + (0, height, 0, height)
        result = re.match(r'(\d{1,4},\d{3}.\d{2})*(\+*\d{1,3},\d{3})*',
                          ''.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)]))
        result_nwt = result.group(1)
        result_tare = result.group(2)

        if result_nwt is not None:
            result_nwt = re.sub(r',*\+*', '', result_nwt)
        else:
            result_nwt = 0
        if result_tare is not None:
            result_tare = re.sub(r',*\+*', '', result_tare)
        else:
            result_tare = 0
        
        list_count_nwt.append(float(result_nwt))
        list_count_tare.append(float(result_tare))

    return list_count_nwt, list_count_tare


def get_container_hazards(total_words, rect_list, rect_add, height):
    list_count = str()
    for rect in rect_list:
        rect = rect + rect_add + (0, height, 0, height)
        list_count += ''.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)]).replace('(NON-HAZARDOUS)', '').strip()
    return list_count.split()      
    

def create_hazards_list(hazards_list:list) -> str:
    unique_list = concatenate_list(hazards_list)
    return ' '.join(set(unique_list)).replace('//', '')
    

def concatenate_floats(*lists:list) -> float:
    concatenated_list = itertools.chain.from_iterable(*lists)
    summa = float(sum(concatenated_list))
    return int(summa)
    

def concatenate_list(*lists):
    return itertools.chain.from_iterable(*lists)


def calculate_weights(weight_list:list, container_list:list) -> float:
    container_amount = concatenate_floats(container_list)
    if container_amount == 0:
        return 0.00
    else:
        return float(concatenate_floats(weight_list))/container_amount


def calculate_vgm(list_nwt, list_tare, list_count):
    return round((calculate_weights(list_nwt, list_count) + calculate_weights(list_tare, list_count)))


def departure_week(etd):
    return str(datetime.strptime(etd, r'%Y/%m/%d').isocalendar().week).zfill(2)


def check_if_dates_match(booking_date, etd):
    booking_date = re.search(r'\d{4}/\d{2}/\d{2}', booking_date).group()
    booking_date = datetime.strptime(booking_date, r'%Y/%m/%d')
    etd = datetime.strptime(etd, r'%Y/%m/%d')
    if booking_date == etd:
        return True
    else:
        return False
    

def extract_final_pod(string):
    # Matches all characters before the first comma after a colon
    pattern = r'^:*(.+?),'
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        return None
    

def trim_date_string(string):
    # Trim date string from 'DATE:' if there is any in the beginning
    pattern= r'\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}'
    matching = re.search(pattern, string)
    if matching:
        return matching.group().strip()
    else:
        return str()
    
def ocean_vessel_and_voy(string):
    # Matching vessel and voyage number from string
    matching = re.match(r'^VSL/VOY:*(\D+)*\s([\d\w-]*)$', string)
    return {'vessel': matching.group(1), 'voy': matching.group(2)}


def cfg_to_dict(config_file: str, section_num: int) -> dict:
    config = configparser.ConfigParser()
    config.read(config_file)

    section = config.sections()[section_num]
    to_dict = dict()
    for key, values in config[section].items():
        crude_list = values.upper().split(',')
        entries_list = list(map(str.strip, crude_list))
        for value in entries_list:
            to_dict[value] = key.upper()
    return to_dict

def map_from_dict(config_file: str, *args:str, section: int) -> str:
    map_dict = cfg_to_dict(config_file, section)
    for key, value in map_dict.items():
        for arg in args:
            if key in arg.upper():
                return value.upper()
    return str()

def navis_voyage(terminal, vessel, departure_date, week) -> str:
    if not terminal:
        return str()
    return f'{vessel}-{departure_date[2:4]}{week}'


if __name__ == '__main__':
    pass