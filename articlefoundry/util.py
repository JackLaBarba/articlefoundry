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

class PlosDoi(object):
    RE_SHORT_DOI_PATTERN = "[a-z]*\.[0-9]*"

    _short_doi = None

    def __init__(self, doi_str):
        self._pub_prefix = "10.1371/journal."

        short_form_match = re.compile(self.RE_SHORT_DOI_PATTERN)
        long_form_match = re.compile('(?<=10\.1371/journal\.)%s' %
                                     self.RE_SHORT_DOI_PATTERN)
        ambra_doi_match = re.compile('^(?<=info\:doi/10\.1371/journal\.)%s$' %
                                     self.RE_SHORT_DOI_PATTERN)

        if short_form_match.match(doi_str):
            self._short_doi = doi_str
            logger.debug("Parsing short form doi: %s" % doi_str)
        elif long_form_match.search(doi_str):
            self._short_doi = long_form_match.search(doi_str).group()
            logger.debug("Parsing long form doi: %s" % doi_str)
        elif ambra_doi_match.search(doi_str):
            self._short_doi = ambra_doi_match.search(doi_str).group()
            logger.debug("Parsing ambra-style doi: %s" % doi_str)
        else:
            raise ValueError("Couldn't parse doi %s" % doi_str)

        logger.debug("Constructed Doi object with shortform doi: %s" % self._short_doi)

    @property
    def short(self):
        return self._short_doi

    @property
    def long(self):
        return "%s%s" % (self._pub_prefix, self._short_doi)

    def __str__(self):
        return self._short_doi


class GOXMLObject(object):
    def __init__(self, xml_file):
        parser = etree.XMLParser(recover=True)
        self.etree = etree.parse(xml_file, parser)

    def get_production_task_id(self):
        prod_ids = self.etree.xpath("//header/parameters/parameter[@name='production-task-id']")
        prod_id = get_single(prod_ids, "guid")
        return prod_id.attrib['value']

    def get_production_task_name(self):
        production_task_names = self.etree.xpath("//header/parameters/parameter[@name='production-task-name']")
        production_task_name = get_single(production_task_names, "production task name")
        return production_task_name.attrib['value']

    def get_metadata_filename(self):
        prod_ids = self.etree.xpath("//filegroup/metadata-file")
        prod_id = get_single(prod_ids, "guid")
        return prod_id.attrib['name']

    def get_doi(self):
        dois = self.etree.xpath("//header/parameters/parameter[@name='DOI']")
        doi = get_single(dois, "DOI")
        return PlosDoi(doi.attrib['value'])

    def get_files(self):
        files = self.etree.xpath("//filegroup/file")
        return [f.attrib['name'] for f in files]



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
                             (ordinal_format(i), self.self_ref_name, si_elem['label']))

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
                             (ordinal_format(i), self.self_ref_name, fig_elem['label']))
            except KeyError:
                logger.error("%s figure in %s, '%s', is missing an href" %
                             (ordinal_format(i), self.self_ref_name, fig_elem['label']))

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


def normalized_find(target_list, key, value, normalizer=None):
    if not normalizer:
        normalizer = lambda x: x

    matches = []
    for index, item in enumerate(target_list):
        if normalizer(item.get(key)) == normalizer(value):
            matches.append(index)

    return matches


def zip_together_assets(expected, adding, matching_level=0, partial_completion=[]):

    if not expected:
        logger.debug("All expected assets found a match.")
        if adding:
            logger.info("I was unable to merge in the following assets due "
                        "to no apparent match in article XML being found: %s" % adding)
        return partial_completion

    if not adding:
        logger.info("Ran out of assets to merge in but I still need matches for"
                    " the following links in the article XML: %s" % expected)
        return partial_completion

    if matching_level == 0:
        matching_level_name = "exact match"
        normalizer = lambda x: x
    elif matching_level == 1:
        matching_level_name = "no-whitespace match"
        normalizer = lambda x: x.replace(" ", "")
    elif matching_level == 2:
        matching_level_name = "case-insensitive, no-whitespace match"
        normalizer = lambda x: x.replace(" ", "").lower()
    elif matching_level == 3:
        matching_level_name = "no-punctuation, case-insensitive, no-whitespace match"
        normalizer = lambda x: x.replace(" ", "").lower().translate(None, string.punctuation)
    else:
        logger.info("I've run out of match relaxations, but there are still assets that need matching.\n"
                    "I'm still expecting assets for these: %s\n"
                    "And I wasn't able to merge in these: %s" %
                    (expected, adding))
        return partial_completion

    expected_match_mask = [0] * len(expected)
    adding_match_mask = [0] * len(expected)

    zippered = partial_completion

    logger.debug("Attempting to match asset files via %s..." % matching_level_name)
    for i, asset in enumerate(expected):
        matches = normalized_find(adding, 'label',
                                  asset.get('label'), normalizer=normalizer)
        if len(matches) == 1:
            logger.debug("Matching %s with %s" % (asset, adding[matches[0]]))
            zippered.append({'expected': asset,
                             'new': adding[matches[0]]})
            expected_match_mask[i] = 1
            adding_match_mask[matches[0]] = 1
        elif len(matches) >= 1:
            logger.error("Found %s SI file matches for %s when I only expected one!" %
                         (len(matches), asset))
            raise ValueError("Found %s SI file matches for %s when I only expected one!" %
                             (len(matches), asset))
        else:
            logger.debug("No SI asset found for %s using %s" % (asset, matching_level_name))

    return zip_together_assets([expected[i] for i in xrange(len(expected)) if not expected_match_mask[i]],
                               [adding[i] for i in xrange(len(adding)) if not adding_match_mask[i]],
                               matching_level+1, zippered)







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
