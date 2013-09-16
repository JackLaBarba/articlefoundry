import re
import zipfile

from lxml import etree

import logging
from logging_config import init_logging
init_logging()
logger = logging.getLogger(__name__)


class Article(object):
    doi = None
    zip_file = None
    xml_orig = None
    xml_orig_tree = None

    def __init__(self, archive_file):
        # Figure out DOI
        logger.debug("Discerning DOI from '%s' ..." % archive_file)
        match = re.match('\w{4}\.\d{7}', archive_file)
        if match:
            self.doi = match.group(0)
            logger.debug("DOI: %s" % self.doi)
        else:
            logger.error("Could not determine doi from filename.")
            return None

        # Open zip file
        try:
            logger.debug("Attempting to open file, %s ..." % archive_file)
            self.zip_file = zipfile.ZipFile(archive_file, 'r')
        except IOError, e:
            logger.error(e)
            return None

        # Identify xml.orig
        orig_filename = "%s.xml.orig" % self.doi
        try:
            self.xml_orig = self.zip_file.open(orig_filename)
        except KeyError, e:
            logger.error("Archive is missing %s" % orig_filename)
            return None

        # Parse xml
        logger.debug("Parsing %s ..." % orig_filename)
        parser = etree.XMLParser(recover=True)
        self.xml_orig_tree = etree.parse(self.xml_orig, parser)
