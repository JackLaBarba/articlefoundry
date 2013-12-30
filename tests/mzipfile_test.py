import os
import shutil

import unittest
from articlefoundry import Article

class TestMZipFile(unittest.TestCase):
    
    def setUp(self):
        self.origin_test_zip = os.path.join(os.path.split(__file__)[0],
                                       'pone.0070111.zip')
        self.test_zip        = os.path.join(os.path.split(__file__)[0],
                                       'pone.0070111.test.zip')
        shutil.copyfile(self.origin_test_zip, self.test_zip)
        self.a = Article(self.test_zip)

    def tearDown(self):
        self.a.close()
        os.remove(self.test_zip)

    def test_mv_move(self):
        new_name = 'lala'
        self.a.zip_file.mv([('pone.0070111.pdf', new_name)])
        print self.a.zip_file.zipfile.namelist()
        self.assertTrue(new_name in self.a.zip_file.zipfile.namelist())

    def test_mv_delete(self):
        new_name = ''
        self.a.zip_file.mv([('pone.0070111.pdf', new_name)])
        print self.a.zip_file.zipfile.namelist()
        self.assertTrue('pone.0070111.pdf' not in self.a.zip_file.zipfile.namelist())
        self.assertTrue('' not in self.a.zip_file.zipfile.namelist())        

    def test_mv_fake(self):
        new_name = 'lala'
        prevlength = len(self.a.zip_file.zipfile.namelist())
        self.a.zip_file.mv([('pone.0070111.pdfnomatch', new_name)])
        print self.a.zip_file.zipfile.namelist()
        self.assertEqual(prevlength, len(self.a.zip_file.zipfile.namelist()))

