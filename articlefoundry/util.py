import re

import logging
import logging_config  # noqa
logger = logging.getLogger(__name__)


def get_pdf_page_count(filename=None, string=None):
    """

    """
    if not file and not string:
        raise ValueError("Need to specify either a file or string for "
                         "get_pdf_page_count")
    if filename:
        pdf_content = file(filename, 'rb').read()
        if string:
            logger.warning("%s supplied with both 'filename' and 'string'."
                           "  Defaulting to 'filename'." % __name__)
    else:
        pdf_content = string

    rx_count_pages = re.compile(r"/Type\s*/Page([^s]|$)",
                                re.MULTILINE | re.DOTALL)

    return len(rx_count_pages.findall(pdf_content))

def normalize_si_label(s):
    return s.strip().replace(' ','').lower().translate(None, string.punctuation)

def get_si_entries(meta_etree):
    """

    """
    pass
    
    
