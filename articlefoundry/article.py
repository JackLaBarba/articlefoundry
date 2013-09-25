import os
import re
import zipfile

from lxml import etree

import util
from mzipfile import MZipFile

import logging
import logging_config  # noqa
logger = logging.getLogger(__name__)


class Article(object):
    doi = None
    # xml trees
    xml_orig_tree = None
    # file streams
    zip_file = None
    xml_orig_file = None
    pdf_file = None

    def __init__(self, archive_file):
        # Figure out DOI
        logger.debug("Discerning DOI from '%s' ..." % archive_file)
        match = re.match('\w{4}\.\d{7}', os.path.split(archive_file)[1])
        if match:
            self.doi = match.group(0)
            logger.debug("DOI: %s" % self.doi)
        else:
            logger.error("Could not determine doi from filename.")
            return None

        # Open zip file
        try:
            logger.debug("Attempting to open file, %s ..." % archive_file)
            self.zip_file = MZipFile(archive_file)
        except IOError, e:
            logger.error(e)
            return None

    def __del__(self):
        self.close()
        # del xml trees
        #  -
        # del file objects
        if self.xml_orig_file:
            del self.xml_orig_file
        if self.zip_file:
            del self.zip_file
        if self.pdf_file:
            del self.pdf_file
            
    def close(self):
        if self.xml_orig_file:
            self.xml_orig_file.close()
        if self.zip_file:
            self.zip_file.close()
        if self.pdf_file:
            self.pdf_file.close()

    def open_xml_orig(self):
        # Identify xml.orig
        orig_filename = "%s.xml.orig" % self.doi
        try:
            self.xml_orig_file = self.zip_file.zipfile.open(orig_filename)
        except KeyError:
            logger.error("Archive is missing %s" % orig_filename)
            return None

    def parse_xml_orig(self):
        # Parse xml.orig
        orig_filename = "%s.xml.orig" % self.doi
        logger.debug("Parsing %s ..." % orig_filename)
        parser = etree.XMLParser(recover=True)
        self.xml_orig_tree = etree.parse(self.xml_orig_file, parser)

    def open_pdf(self):
        self.pdf_file = self.zip_file.zipfile.open("%s.pdf" % self.doi)

    def get_pdf_page_count(self):
        if not self.pdf_file:
            self.open_pdf()
        return util.get_pdf_page_count(string=self.pdf_file.read())
