import os
import shutil

from filetestcase import FileTestCase
from articlefoundry import Article, MetadataPackage
import logging

logger = logging.getLogger(__name__)


class TestArticle(FileTestCase):
    
    def setUp(self):
        self.test_file_dir = os.path.join(os.path.split(__file__)[0], 'files/')
        test_zip = self.backup_file('pone.0077196.zip')
        self.a = Article(test_zip, new_cw_file=True, read_only=True)

        test_zip = self.backup_file('pone_009486b4-32e4-4646-9249-9244544b8719.zip')
        self.m = MetadataPackage(test_zip)

    #TODO Add assertions
    def test_get_pagecount(self):
        self.assertEqual(self.a.get_pdf_page_count(), 17)

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

    def test_consume_si_package(self):
        self.a.consume_si_package(self.m)
        self.a.close()

    def test_check_for_dtd_error(self):
        logger.debug(self.a.check_for_dtd_error())

class TestMetadataPackage(FileTestCase):

    def setUp(self):
        self.test_file_dir = os.path.join(os.path.split(__file__)[0], 'files/')
        test_zip = self.backup_file('pone_3b1d8099-ae81-4fd3-8c72-5ca741bb39d9.zip')
        self.m = MetadataPackage(test_zip)

    def test_parsing(self):
        self.assertEqual(True, True)

    def test_get_doi(self):
        self.assertEqual(self.m.get_doi().long, "10.1371/journal.pone.0074265")


class TestMetadataPackageSI(FileTestCase):

    def setUp(self):
        self.test_file_dir = os.path.join(os.path.split(__file__)[0], 'files/')
        test_zip = self.backup_file('pone_009486b4-32e4-4646-9249-9244544b8719.zip')
        self.m = MetadataPackage(test_zip)

    def test_parsing(self):
        self.assertEqual(True, True)

    def test_get_doi(self):
        self.assertEqual(self.m.get_doi().long, "10.1371/journal.pone.0077196")

    def test_get_si_filenames(self):
        logger.debug(self.m.get_si_filenames())
        files = [{'link': 'Supporting Methods.doc', 'label': 'Methodss1'},
                 {'link': 'Supporting Table S1.doc', 'label': 'Table S1'},
                 {'link': 'Supporting Table S2.doc', 'label': 'TableS2'},
                 {'link': 'Supporting Table S3.doc', 'label': 'TableS3.'}]

        self.assertEquals(self.m.get_si_filenames(), files)

