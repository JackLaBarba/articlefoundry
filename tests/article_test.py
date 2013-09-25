import os

import unittest
from articlefoundry import Article

class TestArticle(unittest.TestCase):
    
    def setUp(self):
        test_zip = os.path.join(os.path.split(__file__)[0], 'pone.0070111.zip')
        self.a = Article(test_zip)

    def test_get_pagecount(self):
        self.assertEqual(self.a.get_pdf_page_count(), 10)

