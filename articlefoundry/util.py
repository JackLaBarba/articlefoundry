import re
import string

import logging
import logging_config  # noqa
logger = logging.getLogger(__name__)


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


def normalize_string(s):
    r = s.strip()
    r = r.replace(' ', '')
    r = r.lower()
    r = r.translate(None, string.punctuation)
    return r


def get_si_links_from_article(article_etree):
    article_links = {}
    for i, si in enumerate(article_etree.xpath("//supplementary-material")):
        try:
            label_raw = si.xpath("label")[0].text
        except IndexError:
            logger.error("%s article SI entry is missing a label" %
                         ordinal_format(i))
            continue

        label = normalize_string(label_raw)
        try:
            link = si.attrib['{http://www.w3.org/1999/xlink}href']
        except KeyError:
            logger.error("%s article SI entry, '%s', is missing an href" %
                         (ordinal_format(i), label_raw))
            link = None

        article_links[label] = link

    return article_links


def get_si_links_from_meta(meta_etree):
    meta_links = {}
    for i, si in enumerate(meta_etree.xpath("//supplementary-material")):
        try:
            label_raw = si.xpath("label")[0].text
        except IndexError:
            logger.error("%s SI entry is missing a label" %
                         ordinal_format(i))
            continue
        label = normalize_string(label_raw)
        if label in meta_links:
            logger.error("Metadata contains more than one SI entry with "
                         "label, %s" % label)
            continue
        try:
            link = si.attrib['{http://www.w3.org/1999/xlink}href']
        except KeyError:
            logger.error("%s SI entry, '%s', is missing an href" %
                         (ordinal_format(i), label_raw))
            link = None

        meta_links[label] = link

    return meta_links


def get_fig_links_from_meta(meta_etree):
    fig_links = {}
    for i, fig in enumerate(meta_etree.xpath("//fig")):
        try:
            label_raw = fig.xpath("label")[0].text
        except IndexError:
            logger.error("%s figure is missing a label" %
                         ordinal_format(i))
            continue

        label = normalize_string(label_raw)
        try:
            graphic = fig.xpath("graphic")[0]
            link = graphic.attrib['{http://www.w3.org/1999/xlink}href']
        except IndexError:
            logger.error("%s figure, '%s', is missing a graphic entry" %
                         (ordinal_format(i), label_raw))
            link = None
        except KeyError:
            logger.error("%s figure, '%s', is missing an href" %
                         (ordinal_format(i), label_raw))
            link = None

        fig_links[label] = link

    return fig_links


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
                             "Failing to rename further occurences." %
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
