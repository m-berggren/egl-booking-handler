
import fitz

from eglhandler.src.parser.constants import *
from eglhandler.src.parser import parser_functions as pf

def get_info():
    PDF_DOC= r'app\eglhandler\src\parser\tests\files\SB9SJRXL.PDF'

    with open(PDF_DOC) as f:
        doc = fitz.open(f)

    total_height = 0.0
    total_words = []
    list_count_40hc, list_count_40dv, list_count_20dv = [], [], []
    list_tare_40hc, list_tare_40dv, list_tare_20dv = [], [], []
    list_nwt_40hc, list_nwt_40dv, list_nwt_20dv = [], [], []
    list_hazards_40hc, list_hazards_40dv, list_hazards_20dv = [], [], []

    for page in doc:
        word_list = page.get_text('words')

        for word in word_list:
            """Add the height of the page to the y coordinates of the words."""
            total_words.append([word[0], word[1] + total_height, word[2], word[3] + total_height, word[4]])
        

        d20 = page.search_for(CONTAINER_20DV)
        d40 = page.search_for(CONTAINER_40DV)
        h40 = page.search_for(CONTAINER_40HC)

        list_count_40hc.append(pf.get_container_amount(total_words, h40, RECT_CONTAINER_HC, total_height))

        total_height += page.rect.height

    return_dict = {
        'pdf_doc': PDF_DOC,
        'total_words': total_words,
        'total_height': total_height,
        'd20': d20,
        'd40': d40,
        'h40': list_count_40hc
        }

    return return_dict

if __name__ == '__main__':
    print(get_info())
