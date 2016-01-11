import unittest
import os
import sys
import json
from helpers import TestHelpers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from application import Application


class ApplicationTest(unittest.TestCase, TestHelpers):

    def test_raises_exception_if_ids_do_not_match(self):
        file_config = self.get_sample_installed_config()
        file_config['id'] = 234
        web_config = self.get_sample_installed_config()
        with self.assertRaises(Exception):
            Application.from_configs(web_config, file_config)

    def test_uses_web_config_name_if_name_do_not_match(self):
        file_config = self.get_sample_installed_config()
        file_config['name'] = 'Bad Wolf'
        web_config = self.get_sample_application_config()
        app = Application.from_configs(web_config, file_config)
        self.assertEquals(web_config['name']['en-us'], app.name)

    def test_has_correct_fields(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
        app = Application.from_configs(web_config, installed_config)

        self.assertEquals(web_config['id'], app.id)
        self.assertEquals(web_config['name']['en-us'], app.name)
        self.assertEquals(installed_config['current_version'], app.current_version)
        self.assertEquals(web_config['available_version'], app.available_version)
        self.assertEquals(web_config['location'], app.download_location)
        self.assertEquals(web_config['install_path'], app.relitive_install_path)
        self.assertEquals(installed_config['installed_path'], app.installed_path)
        self.assertEquals(installed_config['shortcut_path'], app.shortcut_path)
        self.assertEquals(web_config['executable'], app.executable_path)

    def test_two_identical_applications_are_equal(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
        app1 = Application.from_configs(web_config, installed_config)
        app2 = Application.from_configs(web_config, installed_config)
        self.assertEquals(app1, app2)

    def test_actions_should_be_install_if_no_existing_version(self):
        web_config = self.get_sample_application_config()
        app = Application.from_configs(web_config)

        self.assertEquals(1, len(app.actions))
        self.assertEquals('install', app.actions[0])

    def test_actions_should_be_remove_if_version_of_installed_equal_to_new_version(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
        installed_config['current_version'] = '2.3.4'
        web_config['available_version'] = '2.3.4'
        app = Application.from_configs(web_config, installed_config)

        print app.actions
        self.assertEquals(1, len(app.actions))
        self.assertEquals('remove', app.actions[0])

    def test_actions_should_be_remove_and_upgrade_if_version_of_installed_not_equal_to_new_version(self):
        installed_config = self.get_sample_installed_config()
        web_config = self.get_sample_application_config()
        installed_config['current_version'] = '2.3.4'
        web_config['available_version'] = '2.4.4'
        app = Application.from_configs(web_config, installed_config)
        self.assertEquals(2, len(app.actions))
        self.assertTrue('remove' in app.actions)
        self.assertTrue('upgrade' in app.actions)

    def test_get_json_should_return_expected_json(self):
        id = 66
        name = "name"
        available_version = "available_version"
        download_location = "download_location"
        relitive_install_path = "relitive_install_path"
        executable_path = "executable_path"
        installed_path = "installed_path"
        icon = "icon"
        current_version = "current_version"
        shortcut_path = "shortcut_path"
        app = Application(id, name, available_version, download_location, relitive_install_path, executable_path, installed_path, icon, current_version, shortcut_path)
        expected_json = {
                        "id": 66,
                        "name": {
                            "en-us": "name",
                        },
                        "available_version": "available_version",
                        "download_location": "download_location",
                        "relitive_install_path": "relitive_install_path",
                        "executable_path": "executable_path",
                        "installed_path": "installed_path",
                        "icon": "icon",
                        "current_version": "current_version",
                        "shortcut_path": "shortcut_path",
                        }

        actual = json.loads(app.get_json())
        self.assertEquals(expected_json, actual)

    def test_get_json_should_return_expected_json_when_some_fields_are_none(self):
        id = 66
        name = "name"
        available_version = "available_version"
        download_location = "download_location"
        relitive_install_path = "relitive_install_path"
        installed_path = "installed_path"
        icon = "icon"
        shortcut_path = "shortcut_path"
        app = Application(id, name, available_version, download_location, relitive_install_path, None, installed_path, icon, None, shortcut_path)
        expected_json = {
                        "id": 66,
                        "name": {
                            "en-us": "name",
                        },
                        "available_version": "available_version",
                        "download_location": "download_location",
                        "relitive_install_path": "relitive_install_path",
                        "installed_path": "installed_path",
                        "icon": "icon",
                        "shortcut_path": "shortcut_path",
                        }

        actual = json.loads(app.get_json())
        self.assertEquals(expected_json, actual)


if __name__ == '__main__':
    unittest.main()

