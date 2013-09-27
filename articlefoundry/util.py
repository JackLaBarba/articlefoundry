import re
import string

import logging
import logging_config  # noqa
logger = logging.getLogger(__name__)

def ordinal_format(i):
    k=i%10
    return "%d%s"%(i,"tsnrhtdd"[(i/10%10!=1)*(k<4)*k::4])


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


def normalize_string(s):
    r = s.strip()
    r = r.replace(' ', '')
    r = r.lower()
    r = r.translate(None, string.punctuation)
    return r


def get_si_links_from_meta(meta_etree):
    strk_img = {}
    meta_links = {}
    for i, si in enumerate(meta_etree.xpath("//supplementary-material")):
        try:
            label_raw = si.xpath("label")[0].text
        except IndexError, e:
            logger.error("%s SI entry is missing a label" 
                         % ordinal_format(i))
            continue
        label = normalize_string(label_raw)
        if label in meta_links:
            logger.error("Metadata contains more than one SI entry with "
                         "label, %s" % label)
            continue
        try:
            link = si.attrib['{http://www.w3.org/1999/xlink}href']
        except KeyError, e:
            logger.error("%s SI entry, '%s', is missing an href" 
                         % (ordinal_format(i), label_raw))
            link=None
            
        meta_links[label] = link

    return meta_links


def get_fig_links_from_meta(meta_etree):
    fig_links = {}    
    for i, fig in enumerate(meta_etree.xpath("//fig")):
        try:
            label_raw = fig.xpath("label")[0].text
        except IndexError, e:
            logger.error("%s figure is missing a label" 
                         % ordinal_format(i))
            continue

        label = normalize_string(label_raw)
        try:
            link = fig.xpath("graphic")[0].attrib['{http://www.w3.org/1999/xlink}href']
        except IndexError, e:
            logger.error("%s figure, '%s', is missing a graphic entry" 
                         % (ordinal_format(i), label_raw))
            link=None            
        except KeyError, e:
            logger.error("%s figure, '%s', is missing an href" 
                         % (ordinal_format(i), label_raw))
            link=None

        fig_links[label] = link
        
    return fig_links
