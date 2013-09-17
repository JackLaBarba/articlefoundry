import unittest
from articlefoundry import Article

class TestArticle(unittest.TestCase):
    
    def setUp(self):
        self.a = Article('pone.0070111.zip')

    def test_constructor(self):
        pass
