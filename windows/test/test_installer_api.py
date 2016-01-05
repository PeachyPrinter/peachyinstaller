import unittest
import os
import sys
from mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from installer_api import InstallerAPI

@patch('installer_api.urllib2')
class InstallerAPITest(unittest.TestCase):

    def make_mock_response(self, code=200, data=""):
        response = MagicMock()
        response.getcode.return_value = code
        response.read.return_value = data
        return response

    def test_initialize_should_return_a_tuple_and_error_when_internet_unavailable(self, mock_urllib2):
        test_installer_api = InstallerAPI()
        expected_result = (False, 10301, "Connection unavailable")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=404)

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_initialize_should_return_a_setup_files_unavailable_if_cannot_be_parsed(self, mock_urllib2):
        test_installer_api = InstallerAPI()
        expected_result = (False, 10302, "Data File Corrupt or damaged")
        
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data="empty")

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

if __name__ == '__main__':
    unittest.main()