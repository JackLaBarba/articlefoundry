import os
import shutil

from filetestcase import FileTestCase
from articlefoundry import Article
from articlefoundry.file_drivers import ArchiveFile

import logging
logging.basicConfig(level=logging.DEBUG,
                    format=("%(levelname)-8s "
                            "%(message)s"))
logger = logging.getLogger(__name__)

class TestArticleArchiveFile(FileTestCase):

    def setUp(self):
        self.test_file_dir = os.path.join(os.path.split(__file__)[0], 'files/')
        self.origin_test_zip = self.backup_file('pone.0070111.zip')
        self.aaf = ArchiveFile(self.origin_test_zip)

    def test_open(self):
        self.aaf.unzip()
        self.assertTrue(os.path.exists(os.path.join('/tmp/' + self.aaf.uuid)),
                        "Failed to expand zip to tmp")
        logger.debug("open? %s; uuid = %s" % (self.aaf.unzipped, self.aaf.uuid))
        self.aaf.close()
        self.assertFalse(os.path.exists(os.path.join('/tmp/' + self.aaf.uuid)),
                         "Failed to clean up expanded zip in tmp")

    def test_list(self):
        logger.debug(self.aaf.list())

    def test_rename(self):
        self.aaf.unzip()
        self.aaf.rename('manifest.dtd', 'hotdog')
        self.assertTrue('hotdog' in self.aaf.list(), "Unable to rename file")

    def test_rename_nonexistent(self):
        self.assertRaises(KeyError, self.aaf.rename, 'not-a-file', 'does not matter')

    def test_remove(self):
        self.assertTrue(self.aaf.file_exists('manifest.dtd'))
        self.aaf.remove('manifest.dtd')
        self.assertFalse(self.aaf.file_exists('manifest.dtd'),
                         "Failed to remove() file")

