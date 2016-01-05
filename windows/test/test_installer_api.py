import unittest
import os
import sys
import json
from mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from installer_api import InstallerAPI, Application


@patch('installer_api.urllib2')
class InstallerAPITest(unittest.TestCase):

    def get_sample_web_config(self):
        return {
            "id": 1,
            "name": {
                "en-us": "aa",
                },
            "version": "0.1.2",
            "location": "http://someurl",
            "install_path": "bb",
            "executable": "cc.exe",
        }

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

    def test_initialize_should_return_an_error_if_setup_file_valid_but_empty(self, mock_urllib2):
        test_installer_api = InstallerAPI()
        expected_result = (False, 10303, "Config is not valid")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data="[]")

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_initialize_should_return_an_error_if_setup_file_is_incorrect_version(self, mock_urllib2):
        test_installer_api = InstallerAPI()
        expected_result = (False, 10304, "Configuration version too new installer upgrade required")
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data='{"version": 2}')

        result = test_installer_api.initialize()

        self.assertEqual(expected_result, result)

    def test_get_items_should_return_a_list_of_available_items(self, mock_urllib2):
        test_installer_api = InstallerAPI()
        sample = '{"version": 0, "applications":[%s]}' % json.dumps(self.get_sample_web_config())
        expected_result = [Application(self.get_sample_web_config())]
        mock_urllib2.urlopen.return_value = self.make_mock_response(code=200, data=sample)
        init_result = list(test_installer_api.initialize())
        self.assertTrue(init_result[0], init_result[2])

        result = test_installer_api.get_items()

        self.assertEqual(expected_result, result)


class ApplicationTest(unittest.TestCase):

    def get_sample_web_config(self):
        return {
            "id": 1,
            "name": {
                "en-us": "aa",
                },
            "version": "0.1.2",
            "location": "http://someurl",
            "install_path": "bb",
            "executable": "cc.exe",
        }

    def get_sample_installed_config(self):
        return {
            "id": 1,
            "name": {
                "en-us": "aa",
                },
            "version": "0.1.1",
            "installed_path": "bb",
    }

    def test_raises_exception_if_ids_do_not_match(self):
        file_config = self.get_sample_installed_config()
        file_config['id'] = 234
        web_config = self.get_sample_installed_config()
        with self.assertRaises(Exception):
            Application(web_config, file_config)

    def test_uses_web_config_name_if_name_do_not_match(self):
        file_config = self.get_sample_installed_config()
        file_config['name'] = 'Bad Wolf'
        web_config = self.get_sample_web_config()
        app = Application(web_config, file_config)
        self.assertEquals(web_config['name']['en-us'], app.name)

    def test_has_correct_fields(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_web_config()
        app = Application(web_config, installed_config)

        self.assertEquals(web_config['id'], app.id)
        self.assertEquals(web_config['name']['en-us'], app.name)
        self.assertEquals(installed_config['version'], app.current_version)
        self.assertEquals(web_config['version'], app.available_version)
        self.assertEquals(web_config['location'], app.download_location)
        self.assertEquals(web_config['install_path'], app.relitive_install_path)
        self.assertEquals(installed_config['installed_path'], app.full_installed_path)
        self.assertEquals(web_config['executable'], app.executable_path)

    def test_two_identical_applications_are_equal(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_web_config()
        app1 = Application(web_config, installed_config)
        app2 = Application(web_config, installed_config)
        self.assertEquals(app1, app2)

if __name__ == '__main__':
    unittest.main()
