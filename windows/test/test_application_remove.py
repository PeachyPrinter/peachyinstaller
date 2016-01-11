import unittest
import logging
import os
import sys
import time

from helpers import TestHelpers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from application_remove import RemoveApplication
from mock import patch, MagicMock, call


@patch('application_remove.isfile')
@patch('application_remove.isdir')
@patch('application_remove.remove')
@patch('application_remove.rmtree')
class RemoveApplicationTest(unittest.TestCase, TestHelpers):

    def test_start_does_it_right_on_a_happy_path(self, mock_rmtree, mock_remove, mock_isdir, mock_isfile):
        app = self.get_application()
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        status_cb = MagicMock()
        expected_callbacks = ["Initializing", "Removing Application", "Removing Shortcut", "Cleaning up install history", "Finished Removing Files",]
        expected_config_file =  os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', "Peachy", 'PeachyInstaller', 'app-{}.json'.format(app.id))

        RemoveApplication(app, status_cb).start()

        mock_isdir.assert_called_once_with(app.installed_path)
        mock_rmtree.assert_called_once_with(app.installed_path)
        mock_isfile.assert_has_calls([call(app.shortcut_path), call(expected_config_file)])
        mock_remove.assert_has_calls([call(app.shortcut_path), call(expected_config_file)])

        callbacks = [arg[0][0] for arg in status_cb.call_args_list]
        self.assertEqual(expected_callbacks, callbacks)

    def test_start_does_not_delete_shortcut_when_missing(self, mock_rmtree, mock_remove, mock_isdir, mock_isfile):
        app = self.get_application()
        mock_isdir.return_value = True
        is_file_returns = [True, False]
        def side_effect(self):
            return is_file_returns.pop()
        mock_isfile.side_effect = side_effect
        status_cb = MagicMock()
        expected_callbacks = ["Initializing", "Removing Application", "Removing Shortcut", "Shortcut Not Found", "Cleaning up install history", "Finished Removing Files",]
        expected_config_file =  os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', "Peachy", 'PeachyInstaller', 'app-{}.json'.format(app.id))

        RemoveApplication(app, status_cb).start()

        mock_isfile.assert_has_calls([call(app.shortcut_path), call(expected_config_file)])
        mock_remove.assert_has_calls([call(expected_config_file)])

        callbacks = [arg[0][0] for arg in status_cb.call_args_list]
        self.assertEqual(expected_callbacks, callbacks)

    def test_start_does_not_delete_app_when_missing(self, mock_rmtree, mock_remove, mock_isdir, mock_isfile):
        app = self.get_application()
        mock_isdir.return_value = False
        mock_isfile.return_value = True
        status_cb = MagicMock()
        expected_callbacks = ["Initializing", "Removing Application", "Application Not Found", "Removing Shortcut", "Cleaning up install history", "Finished Removing Files",]

        RemoveApplication(app, status_cb).start()

        mock_isdir.assert_called_once_with(app.installed_path)
        self.assertFalse(mock_rmtree.called)

        callbacks = [arg[0][0] for arg in status_cb.call_args_list]
        self.assertEqual(expected_callbacks, callbacks)

    def test_start_does_not_delete_config_when_missing(self, mock_rmtree, mock_remove, mock_isdir, mock_isfile):
        app = self.get_application()
        mock_isdir.return_value = True
        is_file_returns = [False, True]
        def side_effect(self):
            return is_file_returns.pop()
        mock_isfile.side_effect = side_effect
        status_cb = MagicMock()
        expected_callbacks = ["Initializing", "Removing Application", "Removing Shortcut", "Cleaning up install history", "Install history missing", "Finished Removing Files"]

        RemoveApplication(app, status_cb).start()

        self.assertEqual(1, mock_remove.call_count)

        callbacks = [arg[0][0] for arg in status_cb.call_args_list]
        self.assertEqual(expected_callbacks, callbacks)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()