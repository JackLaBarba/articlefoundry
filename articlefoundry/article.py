import os
import re

from lxml import etree

import util
from mzipfile import ArchiveFile

import logging
logging.basicConfig(level=logging.DEBUG,
                    format=("%(levelname)-8s "
                            "%(message)s"))
logger = logging.getLogger(__name__)


class MetadataPackage(object):
    _filename_root = None
    _production_task_id = None

    _goxml_file = None
    _metadata_file = None
    _zip_filename = None

    _archive_file = None
    goxml = None
    metadata = None

    def __init__(self, archive_file):
        try:
            logger.debug("Attempting to open file, %s ..." % archive_file)
            self._archive_file = ArchiveFile(archive_file)
        except IOError, e:
            logger.error(e)
            raise e
        self._zip_filename = archive_file
        self._filename_root = os.path.splitext(os.path.basename(archive_file))[0]
        self._parse_goxml()
        self._parse_metadata()

    def _open_goxml_file(self):
        # Identify go.xml

        goxml_filename = os.path.join(os.path.dirname(self._zip_filename),
                                      "%s.go.xml" % self._filename_root)
        try:
            self._goxml_file = open(goxml_filename, 'r')
        except KeyError, e:
            logger.error("Archive is missing %s" % goxml_filename)
            raise e

    def _parse_goxml(self):
        if not self._goxml_file:
            self._open_goxml_file()
        goxml_filename = "%s.go.xml" % self._filename_root
        logger.debug("Parsing %s ..." % goxml_filename)
        self.goxml = util.GOXMLObject(self._goxml_file)

    def _open_metadata(self):
        # Identify metadata xml
        if not self.goxml:
            self._parse_goxml()
        metadata_filename = self.goxml.get_metadata_filename()
        try:
            self._metadata_file = self._archive_file.get(metadata_filename)
        except KeyError, e:
            logger.error("Archive is missing %s" % metadata_filename)
            raise e

    def _parse_metadata(self):
        # Parse metadata xml
        if not self._metadata_file:
            self._open_metadata()
        metadata_filename = self.goxml.get_metadata_filename()
        logger.debug("Parsing %s ..." % metadata_filename)
        self.metadata = util.MetadataXMLObject(self._metadata_file)

    def get_doi(self):
        if not self.goxml:
            self._parse_goxml()
        return self.goxml.get_doi()

    def is_si_export(self):
        if not self.goxml:
            self._parse_goxml()
        return (self.goxml.get_production_task_name() ==
                "Send Supporting Information Files to PLoS Server")

    def verify_si_export(self):
        if not self.is_si_export():
            raise NotImplementedError("This method doesn't work for this type of export: '%s'" %
                self.goxml.get_production_task_name())

    def get_si_filenames(self):
        self.verify_si_export()
        if not self.metadata:
            self._parse_metadata()
        return sorted(self.metadata.get_si_links(), key=lambda x: x.get('label'))
    
    def __repr__(self):
        return self._zip_filename


class Article(object):
    read_only = False
    doi = None
    # xml trees
    xml_orig_obj = None
    # file streams
    archive_file = None
    xml_orig_file = None
    pdf_file = None

    def __init__(self, archive_file=None, doi=None, new_cw_file=False, read_only=False):
        self.read_only = read_only
        if archive_file:
            self.create_from_archive(archive_file, new_cw_file)
        elif doi:
            self.doi = doi
        else:
            raise ValueError("Article class needs an archive file or a doi "
                             "to make an object")

    def create_from_archive(self, archive_file, new_cw_file=False):
        logger.debug("Discerning DOI from '%s' ..." % archive_file)
        match = re.match('\w{4}\.\d{7}', os.path.split(archive_file)[1])
        if match:
            self.doi = util.PLOSDoi(match.group(0))
            logger.debug("DOI: %s" % self.doi)
        else:
            logger.error("Could not determine doi from filename.")
            return None

        # Open zip file
        try:
            logger.debug("Attempting to open file, %s ..." % archive_file)
            self.archive_file = ArchiveFile(archive_file, read_only=self.read_only)
            self._zip_filename = archive_file
        except IOError, e:
            logger.error(e)
            return None

        if new_cw_file:
            self.archive_file.rename('%s.xml' % self.doi, '%s.xml.orig' % self.doi)

    def __repr__(self):
        return self._zip_filename

    def __del__(self):
        self.close()
        # del xml trees
        #  -
        # del file objects
        if self.xml_orig_file:
            del self.xml_orig_file
        if self.archive_file:
            del self.archive_file
        if self.pdf_file:
            del self.pdf_file

    def close(self):
        if self.xml_orig_file:
            self.xml_orig_file.close()
        if self.archive_file:
            self.archive_file.close()
        if self.pdf_file:
            self.pdf_file.close()

    def open_xml_orig(self):
        # Identify xml.orig
        orig_filename = "%s.xml.orig" % self.doi
        try:
            self.xml_orig_file = self.archive_file.get(orig_filename)
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
        self.pdf_file = self.archive_file.get("%s.pdf" % self.doi)

    def list_package_fig_assets(self):
        files = []
        for f in self.archive_file.zipfile.filelist:
            if re.match("%s\.g\d{3}\.tif" % self.doi,
                        f.filename, re.IGNORECASE):
                files.append(f.filename)
        return files

    def list_package_si_assets(self):
        files = []
        for f in self.archive_file.list():
            if re.match("%s\.s\d{3}\." % self.doi,
                        f, re.IGNORECASE):
                files.append(f)
        return sorted(files)

    def list_expected_fig_assets(self):
        if not self.xml_orig_obj:
            self.parse_xml_orig()
        return sorted(self.xml_orig_obj.get_fig_links(),
                      key=lambda x: x.get('label'))

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

    def check_for_dtd_error(self):
        if not self.xml_orig_file:
            self.open_xml_orig()
        # ensure etree flush first
        return util.XMLObject.check_for_dtd_error(self.xml_orig_file)

    def consume_si_package(self, mdpack):
        logger.info("Attempting to insert SI files from %s to %s ..."  %
                    (mdpack, self))
        if not isinstance(mdpack, MetadataPackage):
            raise ValueError("mdpack needs to be a MetadataPackage object")
        if self.doi != mdpack.get_doi():
            logging.error("SI package doi (%s) does not match article package doi "
                          "(%s).  Exiting ..." % (mdpack.get_doi(), self.doi))
            return
        si_assets = self.list_expected_si_assets()
        logger.debug("Article expects %s SI file(s): %s" % (len(si_assets), si_assets))
        mdpack_si_assets = mdpack.get_si_filenames()
        logger.debug("SI package contains %s SI file(s): %s" % (len(mdpack_si_assets), mdpack_si_assets))
        asset_zipper = util.zip_together_assets(si_assets, mdpack_si_assets)
        asset_zipper.sort(key=lambda x: x['expected']['link'])
        for asset in asset_zipper:
            logger.info("Inserting %s -> %s ..." %
                      (asset['new']['link'], asset['expected']['link']))
            self.archive_file.add(mdpack._archive_file.get(asset['new']['link']),
                              asset['expected']['link'])

        logger.info("Inserted %s file(s) into %s" %
                    (len(asset_zipper), self))
