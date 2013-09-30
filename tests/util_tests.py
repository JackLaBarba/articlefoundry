import os

from lxml import etree

import logging
import articlefoundry.logging_config  # noqa
logger = logging.getLogger(__name__)

import unittest
from articlefoundry.util import *

class TestSIFuncs(unittest.TestCase):
    
    def setUp(self):
        self.meta_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone_PONE-D-13-27833.xml')
        self.meta_file = file(self.meta_filename)
        parser = etree.XMLParser(recover=True)
        self.meta_etree = etree.parse(self.meta_file, parser)

        self.article_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone.0070111.xml.orig')
        self.article_file = file(self.article_filename)
        parser = etree.XMLParser(recover=True)
        self.article_etree = etree.parse(self.article_file, parser)
        
    def test_get_si_links(self):
        logger.debug("SI meta links: %s" % get_si_links_from_meta(self.meta_etree))

    def test_get_fig_links(self):
        logger.debug("FIG links: %s" % get_fig_links_from_meta(self.meta_etree))

    def test_get_article_si_links(self):
        logger.debug("SI article links: %s" % get_si_links_from_article(self.article_etree))

    def test_get_fig_file_mv_list(self):
        doi = 'pone.0012345'
        fig_links_dict = get_fig_links_from_meta(self.meta_etree)
        mv_files = get_fig_file_mv_list(doi, fig_links_dict)
        logger.debug("mv_list: %s" % mv_files)
