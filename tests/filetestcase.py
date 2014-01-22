import shutil
import os
import glob

import unittest


class FileTestCase(unittest.TestCase):

    test_file_dir = None
    backed_up_files = []

    BACKUP_SUFFIX = 'BU'
    TMP_GLOB = '/tmp/af_*'

    def backup_file(self, filename):
        if not self.test_file_dir:
            raise RuntimeError("Need to set instance value for test_file_dir.")

        shutil.copy(os.path.join(self.test_file_dir, filename),
                    os.path.join(self.test_file_dir, filename + self.BACKUP_SUFFIX))

        self.backed_up_files.append(filename)
        return os.path.join(self.test_file_dir, filename)

    def restore_file(self, filename):
        shutil.move(os.path.join(self.test_file_dir, filename + self.BACKUP_SUFFIX),
                    os.path.join(self.test_file_dir, filename))

    def restore_all_files(self):
        while self.backed_up_files:
            f = self.backed_up_files.pop()
            self.restore_file(f)

    def tearDown(self):
        self.restore_all_files()
        self.assertTrue(len(glob.glob(self.TMP_GLOB)) == 0, "Didn't clean up /tmp/")
        super(FileTestCase, self).tearDown()