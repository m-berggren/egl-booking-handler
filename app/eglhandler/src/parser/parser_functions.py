import itertools
import re
from datetime import datetime

import fitz

"""
Functions for pdf_parser file.
"""

def get_value_in_rect(doc, total_words, search_str, rect_add=(0, 0, 0, 0)) -> str:
    """ Return the value of the search_str in the rect_add.
    
    :param doc: The pdf document
    :param total_words: The total words in the pdf
    :param search_str: The string to search for
    :param rect_add: The rectangle to add
    :return: The value of the search_str in the rect_add
    """

    try:
        rect = doc[0].search_for(search_str)[0] + rect_add
    except IndexError:
        return ""

    if rect:
        try:
            return re.match(r'^:*(.*)',' '.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)])).group(1)
        except IndexError:
            return ""

    
def get_container_amount(total_words, rect_list, rect_add, height) -> int:
    """ Return the amount of containers in the rect_list.
    
    :param total_words: The total words in the pdf
    :param rect_list: The list of rectangles
    :param rect_add: The rectangle to add
    :param height: The height of the rectangle
    :return: The amount of containers
    """

    list_count = []
    for rect in rect_list:
        rect = rect + rect_add + (0, height, 0, height)
        result = re.sub(r'^\+*', '',''.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)])).replace(',', '')
        list_count.append(float(result))
    return list_count


def  check_revised_status(revised) -> tuple:
    """ Check if revised is a cancellation or a revision.
    
    :param revised: The revised status
    :return: The revised status and the cancelled status
    """

    cancelled = ""

    if revised == "CANCELLATION":
        cancelled = revised
        revised = 0

    return revised, cancelled
    
    
def get_container_info(total_words, rect_list, rect_add, height) -> tuple:
    """ Return the net weight and tare weight of the containers in the rect_list.
    
    :param total_words: The total words in the pdf
    :param rect_list: The list of rectangles
    :param rect_add: The rectangle to add
    :param height: The height of the rectangle
    :return: The list of net weights and tare weights
    """

    list_count_nwt = []
    list_count_tare = []
    for rect in rect_list:
        rect = rect + rect_add + (0, height, 0, height)

        # Find the net weight and tare weight
        result = re.match(r'((?:\d{1,4},)?\d{1,3},\d{3}\.\d{2}|\d{1,3}\.\d{2})*(\+*\d{1,3},\d{3})*',
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


def get_container_hazards(total_words, rect_list, rect_add, height) -> list:
    """ Return the hazards of the containers in the rect_list.

    :param total_words: The total words in the pdf
    :param rect_list: The list of rectangles
    :param rect_add: The rectangle to add
    :param height: The height of the rectangle
    :return: The list of hazards
    """

    list_count = str()
    for rect in rect_list:
        rect = rect + rect_add + (0, height, 0, height)
        list_count += ''.join([word[4] for word in total_words if fitz.Rect(word[:4]).intersects(rect)]).replace('(NON-HAZARDOUS)', '').strip()
    return list_count.split()
    

def create_string_of_unnos(hazards_list:list) -> str:
    """ Concatenates lists into string and finds all UNNOs.

    :param hazards_list: The hazards list
    :return: Returns a string of IMDG/UNNR separated by commas.
    """

    lists_into_string = concatenate_list(hazards_list)

    if lists_into_string:
        list_all_unnr = re.findall(r"\d*\.*\d\/\d{4}", lists_into_string)
        return ', '.join(set(list_all_unnr))
    else:
        return ""
    

def concatenate_floats(*lists:list) -> int:
    """ Concatenates lists into one list and sums the values.
    
    :param lists: The lists to concatenate
    :return: The sum of the values
    """

    concatenated_list = itertools.chain.from_iterable(*lists)
    summa = float(sum(concatenated_list))
    return int(summa)
    

def concatenate_list(*lists) -> str:
    """ Concatenates lists into one string.
    
    :param lists: The lists to concatenate
    :return: The concatenated string
    """
    new_list = list(itertools.chain.from_iterable(*lists))
    return ''.join(new_list)


def calculate_weights(weight_list:list, container_list:list) -> float:
    """ Calculates the average weight of the containers in the weight_list.
    
    :param weight_list: The weight list
    :param container_list: The container amount list
    :return: The average weight
    """

    container_amount = concatenate_floats(container_list)
    if container_amount == 0:
        return 0.00
    else:
        return float(concatenate_floats(weight_list))/container_amount


def calculate_vgm(list_nwt, list_tare, list_count) -> float:
    """ Calculates the VGM of the containers in the list.
    
    :param list_nwt: The net weight list
    :param list_tare: The tare weight list
    :param list_count: The container amount list
    :return: The VGM
    """
    return round((calculate_weights(list_nwt, list_count) + calculate_weights(list_tare, list_count)))


def departure_week(etd) -> str:
    """ Returns the departure week of the etd.
    
    :param etd: The etd
    :return: The departure week
    """
    return str(datetime.strptime(etd, r'%Y/%m/%d').isocalendar().week).zfill(2)


def check_if_dates_match(booking_date, etd) -> bool:
    """ Checks if the booking date and etd match.
    
    :param booking_date: The booking date
    :param etd: The etd
    :return: True if the dates match, False if not
    """

    booking_date = re.search(r'\d{4}/\d{2}/\d{2}', booking_date).group()
    booking_date = datetime.strptime(booking_date, r'%Y/%m/%d')
    etd = datetime.strptime(etd, r'%Y/%m/%d')
    if booking_date == etd:
        return True
    else:
        return False
    

def extract_final_pod(string) -> str:
    """ Extracts the final pod from string.
    
    :param string: The string to be matched
    :return: The final pod
    """

    # Matches all characters before the first comma after a colon
    pattern = r'^:*(.+?),'
    match = re.search(pattern, string)
    if match:
        return match.group(1)
    else:
        return None
    

def trim_date_string(string) -> str:
    """ Trims date string from 'DATE:' if there is any in the beginning.
    
    :param string: The string to be trimmed
    :return: The trimmed string
    """

    pattern= r'\d{4}/\d{2}/\d{2}\s\d{2}:\d{2}:\d{2}'
    matching = re.search(pattern, string)
    if matching:
        return matching.group().strip()
    else:
        return str()
    
    
def ocean_vessel_and_voy(string) -> dict:
    """ Matching vessel and voyage number from string.

    :param string: The string to be matched
    :return: A dictionary with the vessel and voyage number
    """

    matching = re.match(r'^VSL/VOY:*(\D+)*\s([\d\w-]*)$', string)

    if not matching:
        return {'vessel': None, 'voy': None}

    return {'vessel': matching.group(1), 'voy': matching.group(2)}


def _config_to_new_dict(config: dict, section: str) -> dict:
    """ Inverts the config dictionary to a new dictionary.
    The new dictionary has the values as keys and the keys as values.
    Should only be called from 'map_from_dict' function.
    
    :param config: The config dictionary
    :param section: The section in the config dictionary
    :return: A new dictionary
    """
    
    input_dict = config['parser'].get(section)
    
    output_dict = dict()
    for key, value in input_dict.items():
        if isinstance(value, list):
            for item in value:
                output_dict[item.upper()] = key.upper()
        else:
            output_dict[value.upper()] = key.upper()
    return output_dict


def map_from_dict(config: dict, *args:str, section: str) -> str:
    """ Returns the first matching value from args in dict returned from
    '_config_to_new_dict'.

    :param config: The config dictionary
    :param args: The arguments to be matched
    :param section: The section in the config dictionary
    :return: The first matching value
    """

    map_dict = _config_to_new_dict(config, section)
    for key, value in map_dict.items():
        for arg in args:
            if key in arg.upper():
                return value.upper()
    return str()

def map_from_dict_terminal(config: dict, *args:str, section: str) -> str:
    """ Returns the first matching value from args in dict returned from
    '_config_to_new_dict'.

    :param config: The config dictionary
    :param args: The arguments to be matched
    :param section: The section in the config dictionary
    :return: The first matching value
    """
    print(args)

    map_dict = _config_to_new_dict(config, section)
    for key, value in map_dict.items():
        for arg in args:
            key_found = re.search(f"[^\w]{key}[^\w]", arg.upper())
            if key_found:
                return value.upper()
    return str()


def navis_voyage(terminal, vessel, departure_date, week) -> str:
    """ Returns the voyage number in Navis format {XXX-YYWW}.
    XXX = vessel name, YY = last two digits of the year, WW = week number.
    
    :param terminal: The terminal
    :param vessel: The vessel name
    :param departure_date: The departure date
    :param week: The departure week
    :return: The voyage number in Navis format
    """

    if not terminal:
        return str()
    return f'{vessel}-{departure_date[2:4]}{week}'