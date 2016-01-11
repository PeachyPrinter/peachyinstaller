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


@patch('action_handler.InstallApplication')
class AsyncActionHandlerTest(unittest.TestCase, TestHelpers):
    sleep_time = 0.1
    def test_thread_closes_after_exception(self, mock_InstallApplication):
        thread = AsyncActionHandler("action", self.get_application(), '')
        thread.start()
        thread.join()

    def test_installs_as_expected(self, mock_InstallApplication):
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
        status_cb.assert_called_with("Initializing")
        complete_cb.assert_called_with(True, "Success")

    def test_raises_errors_correctly(self, mock_InstallApplication):
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
        status_cb.assert_called_with("Initializing")
        complete_cb.assert_called_with(False, "Kaboom")




if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
