import re
import string
from lxml import etree

import logging
import logging_config  # noqa

logger = logging.getLogger(__name__)

def get_single(iter, name="element"):
    if len(iter) != 1:
        raise ValueError("Found %s %s(s) when I expected 1!" %
                         (len(iter), name))
    else:
        return iter[0]

def tuplesearch(s, t, normalizer=None):
    if normalizer:
        f_ed = filter(lambda x: normalizer(s) ==
                                normalizer(x[0]), t)
    else:
        f_ed = filter(lambda x: s == x[0], t)
    if f_ed:
        return map(lambda x: x[1], f_ed)
    raise KeyError("%s not found" % s)


def ordinal_format(i):
    k = i % 10
    return "%d%s" % (i, "tsnrhtdd"[(i / 10 % 10 != 1) * (k < 4) * k::4])


def normalize_string(s):
    r = s.strip()
    r = r.replace(' ', '')
    r = r.lower()
    r = r.translate(None, string.punctuation)
    return r


def get_pdf_page_count(filename=None, byte_stream=None):
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


class GOXMLObject(object):
    def __init__(self, xml_file):
        parser = etree.XMLParser(recover=True)
        self.etree = etree.parse(xml_file, parser)

    def get_production_task_id(self):
        prod_ids = self.etree.xpath("//header/parameters/parameter[@name='production-task-id']")
        prod_id = get_single(prod_ids, "guid")
        return prod_id.attrib['value']

class NLMXMLObject(object):
    def __init__(self, xml_file):
        parser = etree.XMLParser(recover=True)
        self.etree = etree.parse(xml_file, parser)
        self.self_ref_name = "NLM XML document"

    def get_si_links(self):
        si_links = []
        for i, si in enumerate(self.etree.xpath("//supplementary-material")):
            si_elem = {}
            try:
                si_elem['label'] = si.xpath("label")[0].text
            except IndexError:
                logger.error("%s %s SI entry is missing a label" %
                             (ordinal_format(i), self.self_ref_name))
                continue

            try:
                si_elem['link'] = si.attrib['{http://www.w3.org/1999/xlink}href']
            except KeyError:
                logger.error("%s %s SI entry, '%s', is missing an href" %
                             (ordinal_format(i), self.self_ref_name, label_raw))

            si_links.append(si_elem)

        return si_links

    def get_fig_links(self):
        fig_links = []
        for i, fig in enumerate(self.etree.xpath("//fig")):
            fig_elem = {}
            try:
                fig_elem['label'] = fig.xpath("label")[0].text
            except IndexError:
                logger.error("%s figure in %s is missing a label" %
                             (ordinal_format(i), self.self_ref_name))
                continue

            try:
                graphic = fig.xpath("graphic")[0]
                fig_elem['link'] = graphic.attrib['{http://www.w3.org/1999/xlink}href']
            except IndexError:
                logger.error("%s figure in %s, '%s', is missing a graphic entry" %
                             (ordinal_format(i), self.self_ref_name, label_raw))
            except KeyError:
                logger.error("%s figure in %s, '%s', is missing an href" %
                             (ordinal_format(i), self.self_ref_name, label_raw))

            fig_links.append(fig_elem)

        return fig_links


class ArticleXMLObject(NLMXMLObject):
    def __init__(self, *args):
        super(ArticleXMLObject, self).__init__(*args)
        self.self_ref_name = "article xml.orig"


class MetadataXMLObject(NLMXMLObject):
    def __init__(self, *args):
        super(MetadataXMLObject, self).__init__(*args)
        self.self_ref_name = "article xml.orig"



def get_fig_file_mv_list(doi, fig_links_dict):
    mv_files = []
    taken_ordinals = []
    striking_image_found = False
    for label, link in fig_links_dict.iteritems():
        ordinal_matches = re.findall(r'\d{1,4}', label)
        if 'strikingimage' in label:
            if striking_image_found:
                logger.error("Found multiple figures identified as "
                             "'striking'.  Ignoring '%s'" %
                             label)
                continue
            striking_image_found = True
            new_name = "%s.strk.tif" % doi
            mv_files.append((link, new_name))
        if ordinal_matches:
            ordinal = ordinal_matches[-1]
            if ordinal in taken_ordinals:
                logger.error("Found two figure labels with number, %s. "
                             "Failing to rename further occurrences." %
                             ordinal)
                continue
            else:
                taken_ordinals.append(ordinal)
        if not ordinal_matches:
            logger.error("Unable to determine figure number from label, '%s'. "
                         "Figure file not renamed" % label)
            continue
        new_name = "%s.g%s.tif" % (doi, ordinal.zfill(3))
        mv_files.append((link, new_name))

    return mv_files
