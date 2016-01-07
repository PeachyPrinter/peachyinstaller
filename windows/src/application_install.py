import threading
import urllib2
import os
import zipfile

import logging
logger = logging.getLogger('peachy')


class InstallerException(Exception):
    def __init__(self, error_code, message):
        super(InstallerException, self).__init__(message)
        logger.error("{} - {}".format(error_code, message))
        self.error_code = error_code


class InstallApplication(threading.Thread):
    def __init__(self, application, base_install_path, status_callback=None, complete_callback=None):
        threading.Thread.__init__(self)
        self._application = application
        self._temp_file_location = os.getenv("TEMP")
        self._status_callback = status_callback
        self._complete_callback = complete_callback
        self.CHUNK_SIZE = 16 * 1024
        self._report_status("Initializing")

    def _report_status(self, message):
        logger.info(message)
        if self._status_callback:
            self._status_callback(message)

    def _report_complete(self, success, message):
        logger.info(message)
        if self._complete_callback:
            self._complete_callback(success, message)

    def _fetch_zip(self, url):
        logger.info("Downloading from: {}".format(url))
        response = urllib2.urlopen(url)
        if response.getcode() != 200:
            raise InstallerException(10501, "Got error {} accessing {}".format(response.getcode(), url))
        file_path = os.path.join(self._temp_file_location, url.split('/')[-1])
        logger.info("Saving to: {}".format(file_path))
        try:
            with open(file_path, 'wb') as zip_file:
                total_read = 0
                while True:
                    chunk = response.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    total_read += len(chunk)
                    logger.debug("Reading chunk: {}".format(total_read))
                    zip_file.write(chunk)
            return file_path
        except IOError:
            raise InstallerException(10502, "Error creating file: {}".format(file_path))

    def _unzip_files(self, file_path, destination):
        logger.info("Unzipping {} into {}".format(file_path, destination))
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file_handle:
                zip_file_handle.extractall(destination)
                return destination
        except Exception as ex:
            logger.error(ex.message)
            raise InstallerException(10502, "Error unzipping file")

    def run(self):
        try:
            self._report_status("Downloading")
            file_path = self._fetch_zip(self._application.download_location)
            self._report_status("Unpacking")
            temp_destination = os.path.join(self._temp_file_location, self._application.name)
            temp_destination = self._unzip_files(file_path, temp_destination)
            self._report_status("Installing")
            self._report_status("Creating Shortcuts")
            self._report_status("Finalizing")
            self._report_complete(True, "Success")
        except InstallerException as ex:
            self._report_complete(False, ex.message)
        except Exception as ex:
            logger.error(ex)
            raise

