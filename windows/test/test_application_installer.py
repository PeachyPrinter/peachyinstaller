import unittest
import os
import sys
import time
import cStringIO
from helpers import TestHelpers

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from application_install import InstallApplication
from mock import patch, MagicMock, mock_open


@patch('application_install.urllib2')
class InstallApplicationTest(unittest.TestCase, TestHelpers):
    sleep_time = 0.1

    def get_mock_response(self, code=200, data="", chunksize=64):
        response = MagicMock()
        response.getcode.return_value = code
        dataString = cStringIO.StringIO(data)
        response.read = dataString.read
        return response

    def test_run_kills_thread_correctly_on_exception(self, mock_urlib2):
        mock_urlib2.urlopen.side_effect = Exception("Failed")
        installer = InstallApplication(self.get_application(), '')
        installer.start()
        time.sleep(self.sleep_time)
        installer.join()

    def test_run_downloads_zip_file_from_correct_path(self, mock_urlib2):
        mock_urlib2.urlopen.return_value = "This is a zip file"
        app = self.get_application()
        installer = InstallApplication(app, '')
        installer.start()
        time.sleep(self.sleep_time)
        installer.join()
        mock_urlib2.urlopen.assert_called_with(app.download_location)

    def test_run_should_report_failure_if_response_is_not_200(self, mock_urlib2):
        mock_urlib2.urlopen.return_value = self.get_mock_response(code=504)
        app = self.get_application()
        mock_complete_callback = MagicMock()
        installer = InstallApplication(app, '', complete_callback=mock_complete_callback)
        installer.start()
        time.sleep(self.sleep_time)
        installer.join()
        mock_complete_callback.assert_called_with(False, "Got error 504 accessing {}".format(app.download_location))

    def test_run_should_report_failure_if_cannot_open_file(self, mock_urlib2):
        mock_urlib2.urlopen.return_value = self.get_mock_response(code=200)
        app = self.get_application()
        mock_complete_callback = MagicMock()
        mock_open_file = mock_open()
        with patch('application_install.open', mock_open_file, create=True):
            mock_open_file.side_effect = IOError("Mock Error")
            installer = InstallApplication(app, '', complete_callback=mock_complete_callback)
            installer.start()
            time.sleep(self.sleep_time)
            installer.join()
        expected_path = os.path.join(os.getenv("TEMP"), app.download_location.split('/')[-1])
        mock_complete_callback.assert_called_with(False, "Error creating file: {}".format(expected_path))

    def test_run_should_save_file(self, mock_urlib2):
        expected_data = "abba" * 1024 * 1024
        mock_urlib2.urlopen.return_value = self.get_mock_response(code=200, data=expected_data)
        app = self.get_application()
        mock_complete_callback = MagicMock()
        mock_open_file = mock_open()
        with patch('application_install.open', mock_open_file, create=True):
            mock_file = mock_open_file.return_value
            mock_open_file.return_value = mock_file
            installer = InstallApplication(app, '', complete_callback=mock_complete_callback)
            installer.start()
            time.sleep(self.sleep_time)
            installer.join()
            actual = ''.join([data[0][0] for data in mock_file.write.call_args_list])
            self.assertEquals(expected_data, actual)

    def test_run_should_repoort_saving_file(self, mock_urlib2):
        expected_data = "abba" * 1024 * 1024
        mock_urlib2.urlopen.return_value = self.get_mock_response(code=200, data=expected_data)
        app = self.get_application()
        mock_complete_callback = MagicMock()
        mock_open_file = mock_open()
        with patch('application_install.open', mock_open_file, create=True):
            mock_file = mock_open_file.return_value
            mock_open_file.return_value = mock_file
            installer = InstallApplication(app, '', complete_callback=mock_complete_callback)
            installer.start()
            time.sleep(self.sleep_time)
            installer.join()
            actual = ''.join([data[0][0] for data in mock_file.write.call_args_list])
            self.assertEquals(expected_data, actual)


    def test_run_should_report_steps(self, mock_urlib2):
        mock_status_callback = MagicMock()
        expected_calls = ["Initializing", "Downloading", "Unpacking", "Installing", "Creating Shortcuts", "Finalizing"]
        mock_urlib2.urlopen.return_value = self.get_mock_response(code=200)
        app = self.get_application()
        mock_open_file = mock_open()
        with patch('application_install.open', mock_open_file, create=True):
            mock_file = mock_open_file.return_value
            mock_open_file.return_value = mock_file
            installer = InstallApplication(app, '', status_callback=mock_status_callback)
            installer.start()
            time.sleep(self.sleep_time)
            
            calls = [call[0][0] for call in mock_status_callback.call_args_list]
            actual = ''.join([data[0][0] for data in mock_file.write.call_args_list])
            self.assertEquals(expected_calls, calls)


if __name__ == '__main__':
    unittest.main()

