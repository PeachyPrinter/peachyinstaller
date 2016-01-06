import threading
import urllib2
import os


class InstallerException(Exception):
    def __init__(self, error_code, message):
        super(InstallerException, self).__init__(message)
        self.error_code = error_code


class InstallApplication(threading.Thread):
    def __init__(self, application, base_install_path, status_callback=None, complete_callback=None):
        threading.Thread.__init__(self)
        self._application = application
        self._temp_file_location = os.getenv("TEMP")
        self._status_callback = status_callback
        self._complete_callback = complete_callback
        self.CHUNK_SIZE = 16 * 1024

    def _fetch_zip(self, url):
        response = urllib2.urlopen(url)
        if response.getcode() != 200:
            raise InstallerException(10501, "Got error {} accessing {}".format(response.getcode(), url))
        file_path = os.path.join(self._temp_file_location, url.split('/')[-1])
        try:
            with open(file_path, 'wb') as zip_file:
                while True:
                    chunk = response.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    zip_file.write(chunk)
        except IOError:
            raise InstallerException(10502, "Error creating file: {}".format(file_path))

    def run(self):
        try:
            self._fetch_zip(self._application.download_location)
            self._complete_callback(True, "Success")
        except InstallerException as ex:
            if self._complete_callback:
                self._complete_callback(False, ex.message)

