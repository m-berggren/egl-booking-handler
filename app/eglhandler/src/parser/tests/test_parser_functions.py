import fitz

from eglhandler.src.parser import parser_functions
from eglhandler.src.parser.constants import *
from eglhandler.src.parser.tests.files.parse_pdf import get_info

data = get_info()
PDF_DOC = fitz.Document(data['pdf_doc'])
TOTAL_WORDS = data['total_words']
TOTAL_HEIGHT = data['total_height']
D20 = data['d20']
D40 = data['d40']
H40 = data['h40']

    
def test_get_value_in_rect():
    assert parser_functions.get_value_in_rect(
        PDF_DOC,
        TOTAL_WORDS,
        FINAL_POD,
        RECT_FINAL_POD
    )== 'HO CHI MINH,SOCIALIST REPUBLIC OF VIETNAM'

def test_get_container_amount():
    # TODO: Implement test
    pass

def test_check_revised_status():
    # TODO: Implement test
    pass

def test_get_container_info():
    # TODO: Implement test
    pass

def test_get_container_hazards():
    # TODO: Implement test
    pass

def test_create_string_of_unnos():
    # TODO: Implement test
    pass

def test_concatenate_list():
    # TODO: Implement test
    pass

def test_calculate_weights():
    # TODO: Implement test
    pass

def test_calculate_vgm():
    # TODO: Implement test
    pass

def test_departure_week():
    # TODO: Implement test
    pass

def test_check_if_dates_match():
    # TODO: Implement test
    pass

def test_extract_final_pod():
    # TODO: Implement test
    pass

def test_trim_date_string():
    # TODO: Implement test
    pass

def test_ocean_vessel_and_voy():
    # TODO: Implement test
    pass

def test_cfg_to_dict():
    # TODO: Implement test
    pass

def test_map_from_dict():
    # TODO: Implement test
    pass

def test_navis_voyage():
    # TODO: Implement test
    pass

test_get_container_amount()