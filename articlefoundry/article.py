import os
import re

from lxml import etree

import util
from mzipfile import MZipFile

import logging
import logging_config  # noqa
logger = logging.getLogger(__name__)


class MetadataPackage(object):
    _filename_root = None
    _production_task_id = None

    _goxml_file = None
    _zip_filename = None

    goxml = None
    zip_file = None

    def __init__(self, archive_file):
        try:
            logger.debug("Attempting to open file, %s ..." % archive_file)
            self._zip_file = MZipFile(archive_file)
        except IOError, e:
            logger.error(e)
            raise e
        self._zip_filename = archive_file
        self._filename_root = os.path.splitext(os.path.basename(archive_file))[0]
        self.parse_goxml()

    def open_goxml_file(self):
        # Identify go.xml

        goxml_filename = os.path.join(os.path.dirname(self._zip_filename),
                                      "%s.go.xml" % self._filename_root)
        try:
            self._goxml_file = open(goxml_filename, 'r')
        except KeyError, e:
            logger.error("Archive is missing %s" % goxml_filename)
            raise e

    def parse_goxml(self):
        if not self._goxml_file:
            self.open_goxml_file()
        goxml_filename = "%s.go.xml" % self._filename_root
        logger.debug("Parsing %s ..." % goxml_filename)
        self.goxml = util.GOXMLObject(self._goxml_file)

    def open_metadata(self):
        # Identify metadata xml
        if not self.goxml:
            self.parse.goxml
        metadata_filename = self.goxml.get_metadata_xml
        try:
            self.xml_orig_file = self.zip_file.zipfile.open(orig_filename)
        except KeyError, e:
            logger.error("Archive is missing %s" % orig_filename)
            raise e

    def parse_metadata(self):
        # Parse xml.orig
        if not self.xml_orig_file:
            self.open_xml_orig()
        orig_filename = "%s.xml.orig" % self.doi
        logger.debug("Parsing %s ..." % orig_filename)
        self.xml_orig_obj = util.ArticleXMLObject(self.xml_orig_file)


class Article(object):
    doi = None
    # xml trees
    xml_orig_obj = None
    # file streams
    zip_file = None
    xml_orig_file = None
    pdf_file = None

    def __init__(self, archive_file=None, doi=None):
        if archive_file:
            self.create_from_archive(archive_file)
        elif doi:
            self.doi = doi
        else:
            raise ValueError("Article class needs an archive file or a doi "
                             "to make an object")

    def create_from_archive(self, archive_file):
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
        except KeyError, e:
            logger.error("Archive is missing %s" % orig_filename)
            raise e

    def parse_xml_orig(self):
        # Parse xml.orig
        if not self.xml_orig_file:
            self.open_xml_orig()
        orig_filename = "%s.xml.orig" % self.doi
        logger.debug("Parsing %s ..." % orig_filename)
        self.xml_orig_obj = util.ArticleXMLObject(self.xml_orig_file)

    def open_pdf(self):
        self.pdf_file = self.zip_file.zipfile.open("%s.pdf" % self.doi)

    def list_package_fig_assets(self):
        files = []
        for f in self.zip_file.zipfile.filelist:
            if re.match("%s\.g\d{3}\.tif" % self.doi,
                        f.filename, re.IGNORECASE):
                files.append(f.filename)
        return files

    def list_package_si_assets(self):
        files = []
        for f in self.zip_file.zipfile.filelist:
            if re.match("%s\.s\d{3}\." % self.doi,
                        f.filename, re.IGNORECASE):
                files.append(f.filename)
        return files

    def list_expected_fig_assets(self):
        if not self.xml_orig_obj:
            self.parse_xml_orig()
        return self.xml_orig_obj.get_fig_links()

    def list_expected_si_assets(self):
        if not self.xml_orig_obj:
            self.parse_xml_orig()
        return self.xml_orig_obj.get_si_links()

    def list_missing_si_assets(self):
        expected = set([f['link'] for f in self.list_expected_si_assets()])
        present = set(self.list_package_si_assets())
        return list(expected - present)

    def get_pdf_page_count(self):
        if not self.pdf_file:
            self.open_pdf()
        return util.get_pdf_page_count(byte_stream=self.pdf_file.read())
