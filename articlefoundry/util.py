from __future__ import with_statement
import re
import os
import glob
import string
import urllib2

import logging
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


def download_file(url, local):
    # Open the url
    logger.debug("Dowloading %s to %s..." % (url, local))
    f = urllib2.urlopen(url)

    # Open our local file for writing
    with open(local, "wb") as local_file:
        local_file.write(f.read())


def find_si_guid(doi, locations=None):
    logger.debug("Finding SI GUID ... ")
    if not locations:
        locations = ['/var/spool/delivery/',
                     '/var/spool/delivery-archive/']
    for directory in locations:
        for filename in glob.glob(os.path.join(directory, "*.go.xml")):
            with open(filename, 'r') as f:
                for l in f.readlines():
                    if doi in l:
                        return os.path.abspath(filename)


def normalized_find(target_list, key, value, normalizer=None):
    if not normalizer:
        normalizer = lambda x: x

    matches = []
    for index, item in enumerate(target_list):
        if normalizer(item.get(key)) == normalizer(value):
            matches.append(index)

    return matches


def zip_together_assets(expected, adding, matching_level=0, partial_completion=[]):

    # START handling base cases
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
    # END handling base cases

    expected_match_mask = [0] * len(expected)
    adding_match_mask = [0] * len(expected)

    logger.debug("Attempting to match asset files via %s..." % matching_level_name)
    for i, asset in enumerate(expected):
        matches = normalized_find(adding, 'label',
                                  asset.get('label'), normalizer=normalizer)
        if len(matches) == 1:
            logger.debug("Matching %s with %s" % (asset, adding[matches[0]]))
            partial_completion.append({'expected': asset,
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
                               matching_level+1, partial_completion)


class PLOSDoi(object):
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

        logger.debug("Constructed Doi object with short-form doi: %s" % self._short_doi)

    def __cmp__(self, other):
        return (self._short_doi == other)

    @property
    def short(self):
        return self._short_doi

    @property
    def long(self):
        return "%s%s" % (self._pub_prefix, self._short_doi)

    def __str__(self):
        return self._short_doi
