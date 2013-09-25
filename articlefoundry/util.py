import re
import string

import logging
import logging_config  # noqa
logger = logging.getLogger(__name__)


def get_pdf_page_count(filename=None, byte_stream=None):
    """

    """
    if not file and not byte_stream:
        raise ValueError("Need to specify either a file or string for "
                         "get_pdf_page_count")
    if filename:
        pdf_content = file(filename, 'rb').read()
        if string:
            logger.warning("%s supplied with both 'filename' and 'string'."
                           "  Defaulting to 'filename'." % __name__)
    else:
        pdf_content = byte_stream

    rx_count_pages = re.compile(r"/Type\s*/Page([^s]|$)",
                                re.MULTILINE | re.DOTALL)

    return len(rx_count_pages.findall(pdf_content))


def normalize_si_label(s):
    r = s.strip()
    r = r.replace(' ', '')
    r = r.lower()
    r = r.translate(None, string.punctuation)
    return r


def get_si_entries(meta_etree):
    """

    """
    pass
