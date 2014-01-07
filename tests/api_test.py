import unittest
import logging
logger = logging.getLogger(__name__)

from articlefoundry.api import AIapi

class TestAIapi(unittest.TestCase):

    def setUp(self):
        self.ai = AIapi()

    def tearDown(self):
        self.ai.close()

    def test_get_si_guid(self):
        self.assertIsNotNone(self.ai.get_si_guid('pone.0083652'))
        self.assertRaises(KeyError, self.ai.get_si_guid, 'pone.0083652DOESNTEXIST')
