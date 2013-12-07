import os

import unittest
from articlefoundry import Article
import logging
import articlefoundry.logging_config  # noqa

logger = logging.getLogger(__name__)


class TestArticle(unittest.TestCase):
    
    def setUp(self):
        test_zip = os.path.join(os.path.split(__file__)[0], 'pone.0070111.zip')
        self.a = Article(test_zip)

    def test_get_pagecount(self):
        self.assertEqual(self.a.get_pdf_page_count(), 10)

    def test_list_expected_fig_assets(self):
        logger.debug("Expected fig assets: %s" % self.a.list_expected_fig_assets())

    def test_list_expected_si_assets(self):
        logger.debug("Expected si assets: %s" % self.a.list_expected_si_assets())

    def test_list_package_fig_assets(self):
        logger.debug("Package fig assets: %s" % self.a.list_package_fig_assets())

    def test_list_package_si_assets(self):
        logger.debug("Package si assets: %s" % self.a.list_package_si_assets())

    def test_list_missing_si_assets(self):
        logger.debug("Missing si assets: %s" % self.a.list_missing_si_assets())