import unittest
import logging
import os
import sys
import time
from helpers import TestHelpers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from action_handler import AsyncActionHandler
from action_base import ActionHandlerException
from mock import patch, MagicMock


@patch('action_handler.RemoveApplication')
@patch('action_handler.InstallApplication')
class AsyncActionHandlerTest(unittest.TestCase, TestHelpers):
    sleep_time = 0.1
    def test_thread_closes_after_exception(self, mock_InstallApplication, mock_RemoveApplication):
        thread = AsyncActionHandler("action", self.get_application(), '')
        thread.start()
        thread.join()

    def test_installs_as_expected(self, mock_InstallApplication, mock_RemoveApplication):
        app = self.get_application()
        base_path = 'apath'
        status_cb = MagicMock()
        complete_cb = MagicMock()

        thread = AsyncActionHandler("install", app, base_path, status_cb, complete_cb)
        thread.start()
        time.sleep(self.sleep_time)
        thread.join()

        mock_InstallApplication.assert_called_with(app, base_path, status_callback=status_cb)
        mock_InstallApplication.return_value.start.assert_called_with()
        self.assertFalse(mock_RemoveApplication.called)
        status_cb.assert_called_with("Complete")
        complete_cb.assert_called_with(True, "Success")

    def test_raises_errors_correctly(self, mock_InstallApplication, mock_RemoveApplication):
        app = self.get_application()
        base_path = 'apath'
        status_cb = MagicMock()
        complete_cb = MagicMock()
        mock_InstallApplication.return_value.start.side_effect = ActionHandlerException(1, "Kaboom")

        thread = AsyncActionHandler("install", app, base_path, status_cb, complete_cb)
        thread.start()
        time.sleep(self.sleep_time)
        thread.join()

        mock_InstallApplication.assert_called_with(app, base_path, status_callback=status_cb)
        mock_InstallApplication.return_value.start.assert_called_with()
        self.assertFalse(mock_RemoveApplication.called)
        status_cb.assert_called_with("Failed")
        complete_cb.assert_called_with(False, "Kaboom")

    def test_removes_as_expected(self, mock_InstallApplication, mock_RemoveApplication):
        app = self.get_application()
        base_path = 'apath'
        status_cb = MagicMock()
        complete_cb = MagicMock()

        thread = AsyncActionHandler("remove", app, base_path, status_cb, complete_cb)
        thread.start()
        time.sleep(self.sleep_time)
        thread.join()

        mock_RemoveApplication.assert_called_with(app, status_callback=status_cb)
        mock_RemoveApplication.return_value.start.assert_called_with()
        self.assertFalse(mock_InstallApplication.called)

        status_cb.assert_called_with("Complete")
        complete_cb.assert_called_with(True, "Success")

    def test_upgrades_as_expected(self, mock_InstallApplication, mock_RemoveApplication):
        app = self.get_application()
        base_path = 'apath'
        status_cb = MagicMock()
        complete_cb = MagicMock()

        thread = AsyncActionHandler("upgrade", app, base_path, status_cb, complete_cb)
        thread.start()
        time.sleep(self.sleep_time)
        thread.join()

        mock_RemoveApplication.assert_called_with(app, status_callback=status_cb)
        mock_RemoveApplication.return_value.start.assert_called_with()
        mock_InstallApplication.assert_called_with(app, base_path, status_callback=status_cb)
        mock_InstallApplication.return_value.start.assert_called_with()

        status_cb.assert_called_with("Complete")
        complete_cb.assert_called_with(True, "Success")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
