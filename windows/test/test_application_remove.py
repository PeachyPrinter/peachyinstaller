import unittest
import logging
import os
import sys
import time

from helpers import TestHelpers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from application_install import InstallApplication
from application import Application
from mock import patch, MagicMock, mock_open


@patch('application_install.isdir')
@patch('application_install.listdir')
class RemoveApplicationTest(unittest.TestCase, TestHelpers):
    sleep_time = 0.1

    def get_mock_response(self, code=200, data="", chunksize=64):
        response = MagicMock()
        response.getcode.return_value = code
        dataString = cStringIO.StringIO(data)
        response.read = dataString.read
        return response

    # def test_run_kills_thread_correctly_on_exception(self, mock_urlib2, mock_ZipFile, mock_move, mock_listdir, mock_isdir, mock_create_shortcut):
    #     mock_urlib2.urlopen.side_effect = Exception("Failed")
    #     installer = InstallApplication(self.get_application(), '')
    #     installer.start()
    #     time.sleep(self.sleep_time)
    #     installer.join()