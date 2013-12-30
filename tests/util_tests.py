import os
import lxml

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
        self.meta_xml = MetadataXMLObject(self.meta_file)

        self.article_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone.0070111.xml.orig')
        self.article_file = file(self.article_filename)
        self.article_xml = ArticleXMLObject(self.article_file)

        self.goxml_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone_3b1d8099-ae81-4fd3-8c72-5ca741bb39d9.go.xml')
        self.goxml_file = file(self.goxml_filename)
        self.goxml_xml = GOXMLObject(self.goxml_file)
        
    def test_get_si_links(self):
        logger.debug("SI meta links: %s" % self.meta_xml.get_si_links())

    def test_get_fig_links(self):
        logger.debug("FIG links: %s" % self.meta_xml.get_fig_links())

    def test_get_article_si_links(self):
        logger.debug("SI article links: %s" % self.article_xml.get_si_links())

    def test_get_production_task_id(self):
        self.assertEquals(self.goxml_xml.get_production_task_id(),
                          "3b1d8099-ae81-4fd3-8c72-5ca741bb39d9")

    def test_get_metadata_filename(self):
        self.assertEquals(self.goxml_xml.get_metadata_filename(),
                          "pone_PONE-D-13-27833.xml")

    def test_get_files(self):
        figs = ['Figure7.tif', 'Figure2.tif', 'Figure5.tif', 'Figure3.tif',
                'TableS1_Sampling Conditions.pdf', 'newton.docx', 'Figure1.tif',
                'STable2_TaxonomyTable.pdf', 'Figure S1.tif', 'Figure6.tif',
                'TableS2_TaxonomyTable.pdf', 'Figure4.tif']

        self.assertEquals(self.goxml_xml.get_files(), figs)

    def test_get_production_task_name(self):
        self.assertEquals(self.goxml_xml.get_production_task_name(),
                          "Merops Send to Production - Author Notification")


class TestXMLParsing(unittest.TestCase):

    def test_dtd_invalid(self):
        article_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone.0070111-dtd-invalid.xml.orig')
        article_file = file(article_filename)
        ArticleXMLObject(article_file)

    def test_check_for_dtd_error(self):
        article_filename = os.path.join(os.path.split(__file__)[0],
                                      'pone.0070111-dtd-invalid.xml.orig')
        article_file = file(article_filename)
        output = XMLObject.check_for_dtd_error(article_file)
        logger.debug(output)
        assert output
