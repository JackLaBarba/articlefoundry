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
        self.meta_xml = ArticleXMLObject(self.meta_file)

        self.article_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone.0070111.xml.orig')
        self.article_file = file(self.article_filename)
        self.article_xml = ArticleXMLObject(self.article_file)
        
    def test_get_si_links(self):
        logger.debug("SI meta links: %s" % self.meta_xml.get_si_links())

    def test_get_fig_links(self):
        logger.debug("FIG links: %s" % self.meta_xml.get_fig_links())

    def test_get_article_si_links(self):
        logger.debug("SI article links: %s" % self.article_xml.get_si_links())

"""
    def test_get_fig_file_mv_list(self):
        doi = 'pone.0012345'
        fig_links_dict = self.meta_xml.get_fig_links()
        mv_files = get_fig_file_mv_list(doi, fig_links_dict)
        logger.debug("mv_list: %s" % mv_files)
"""