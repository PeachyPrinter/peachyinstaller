import unittest
import os
import sys
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

