import unittest
import os
import sys
import json
from mock import patch, MagicMock, mock_open
from helpers import TestHelpers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from installer_api import InstallerAPI
from application import Application


@patch.object(os.path, 'exists')
@patch('installer_api.urllib2')
class InstallerAPITest(unittest.TestCase, TestHelpers):

    def make_mock_response(self, code=200, data=""):
        response = MagicMock()
        response.getcode.return_value = code
        response.read.return_value = data
        return response

    def test_initialize_should_return_a_tuple_and_error_when_internet_unavailable(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        test_installer_api = InstallerAPI()
        expected_result = (False, 10301, "Connection unavailable")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=404)

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_initialize_should_return_a_setup_files_unavailable_if_cannot_be_parsed(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        test_installer_api = InstallerAPI()
        expected_result = (False, 10302, "Web data File Corrupt or damaged")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data="empty")

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_initialize_should_return_an_error_if_setup_file_valid_but_empty(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        test_installer_api = InstallerAPI()
        expected_result = (False, 10303, "Config is not valid")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data="[]")

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_initialize_should_return_an_error_if_setup_file_is_incorrect_version(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        test_installer_api = InstallerAPI()
        expected_result = (False, 10304, "Configuration version too new installer upgrade required")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data='{"version": 2}')

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_initialize_should_call_provided_url(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        test_url = "This is a URL"
        test_installer_api = InstallerAPI(test_url)
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data='{"version": 2}')
        test_installer_api.initialize()

        mock_urllib2.urlopen.assert_called_with(test_url)

    def test_get_items_should_return_a_list_of_available_items(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        test_installer_api = InstallerAPI()
        sample = '{"version": 0, "applications":[%s]}' % json.dumps(self.get_sample_application_config())
        expected_result = [Application(self.get_sample_application_config())]
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data=sample)
        init_result = list(test_installer_api.initialize())
        self.assertTrue(init_result[0], init_result[2])

        result = test_installer_api.get_items()

        self.assertEqual(expected_result, result)

    def test_initialize_if_file_config_exists_and_is_inaccessable(self, mock_urllib2, mock_exists):
        mock_exists.return_value = True
        expected_result = (False, 10401, "Install File Inaccessable")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data=self.get_sample_web_config())
        mock_open_file = mock_open()
        with patch('installer_api.open', mock_open_file, create=True):
            mock_open_file.side_effect = IOError("Mock Error")
            test_installer_api = InstallerAPI()
            result = test_installer_api.initialize()
            self.assertEquals(expected_result, result)

    def test_initialize_if_file_config_exists_and_is_not_json(self, mock_urllib2, mock_exists):
        mock_exists.return_value = True
        expected_result = (False, 10402, "Install File Corrupt or Damaged")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data=self.get_sample_web_config())
        mock_open_file = mock_open(read_data="Not Json")
        with patch('installer_api.open', mock_open_file, create=True):
            mock_open_file.read = IOError("Mock Error")
            test_installer_api = InstallerAPI()
            result = test_installer_api.initialize()
            self.assertEquals(expected_result, result)

    def test_initialize_should_create_correct_application(self, mock_urllib2, mock_exists):
        mock_exists.return_value = True
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data=self.get_sample_web_config())
        mock_open_file = mock_open(read_data=self.get_sample_file_config())
        expected_app = Application(self.get_sample_application_config(), self.get_sample_installed_config())

        with patch('installer_api.open', mock_open_file, create=True):
            mock_open_file.read = IOError("Mock Error")
            test_installer_api = InstallerAPI()

            result = test_installer_api.initialize()
            self.assertTrue(result[0])
            apps = test_installer_api.get_items()

            self.assertEquals(1, len(apps))
            self.assertEquals(expected_app, apps[0])

    def test_get_item_responds_with_specific_application(self, mock_urllib2, mock_exists):
        mock_exists.return_value = False
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data=self.get_sample_web_config())
        expected_app = Application(self.get_sample_application_config())
        test_installer_api = InstallerAPI()

        result = test_installer_api.initialize()
        self.assertTrue(result[0])
        app = test_installer_api.get_item(expected_app.id)

        self.assertEquals(expected_app, app)


if __name__ == '__main__':
    unittest.main()

