import unittest
import os
import sys
import json
from mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from installer_api import InstallerAPI, Application


class TestHelpers(object):
    def get_sample_application_config(self):
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

    def get_sample_web_config(self):
        return '{"version": 0, "applications":[%s]}' % json.dumps(self.get_sample_application_config())

    def get_sample_installed_config(self):
        return {
            "id": 1,
            "name": {
                "en-us": "aa",
                },
            "version": "0.1.1",
            "installed_path": "bb",
    }

    def get_sample_file_config(self):
        return '{"version": 0, "applications":[%s]}' % json.dumps(self.get_sample_installed_config())


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

class ApplicationTest(unittest.TestCase, TestHelpers):

    def test_raises_exception_if_ids_do_not_match(self):
        file_config = self.get_sample_installed_config()
        file_config['id'] = 234
        web_config = self.get_sample_installed_config()
        with self.assertRaises(Exception):
            Application(web_config, file_config)

    def test_uses_web_config_name_if_name_do_not_match(self):
        file_config = self.get_sample_installed_config()
        file_config['name'] = 'Bad Wolf'
        web_config = self.get_sample_application_config()
        app = Application(web_config, file_config)
        self.assertEquals(web_config['name']['en-us'], app.name)

    def test_has_correct_fields(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
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
        web_config = self.get_sample_application_config()
        app1 = Application(web_config, installed_config)
        app2 = Application(web_config, installed_config)
        self.assertEquals(app1, app2)

    def test_actions_should_be_install_if_no_existing_version(self):
        web_config = self.get_sample_application_config()
        app = Application(web_config)

        self.assertEquals(1, len(app.actions))
        self.assertEquals('install', app.actions[0])

    def test_actions_should_be_remove_if_version_of_installed_equal_to_new_version(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
        installed_config['version'] = '2.3.4'
        web_config['version'] = '2.3.4'
        app = Application(web_config, installed_config)

        self.assertEquals(1, len(app.actions))
        self.assertEquals('remove', app.actions[0])

    def test_actions_should_be_remove_and_upgrade_if_version_of_installed_not_equal_to_new_version(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
        installed_config['version'] = '2.3.4'
        web_config['version'] = '2.4.4'
        app = Application(web_config, installed_config)
        self.assertEquals(2, len(app.actions))
        self.assertTrue('remove' in app.actions)
        self.assertTrue('upgrade' in app.actions)


if __name__ == '__main__':
    unittest.main()

