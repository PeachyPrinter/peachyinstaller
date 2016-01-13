import urllib2
import os
from os import listdir
from os.path import isdir
import zipfile
from shutil import move
import logging
from win32com.client import Dispatch
import pythoncom


from application import Application
from action_base import ActionHandler, ActionHandlerException

logger = logging.getLogger('peachy')


class ShortCutter(object):
    @staticmethod
    def create_shortcut(destination_file, target_exe, working_dir, icon_file, ):
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(destination_file)
        shortcut.Targetpath = target_exe
        shortcut.WorkingDirectory = working_dir
        shortcut.IconLocation = icon_file
        shortcut.save()


class InstallApplication(ActionHandler):
    def __init__(self, application, base_install_path, status_callback=None):
        self._application = application
        self._base_path = base_install_path
        self._temp_file_location = os.getenv("TEMP")
        self._status_callback = status_callback
        self.CHUNK_SIZE = 16 * 1024
        self._report_status("Initializing")

    def _fetch_zip(self, url):
        logger.info("Downloading from: {}".format(url))
        try:
            response = urllib2.urlopen(url)
        except Exception as ex:
            logger.error(ex)
            raise ActionHandlerException(10507, 'Could not find application at specified URL')
        if response.getcode() != 200:
            raise ActionHandlerException(10501, "Got error {} accessing {}".format(response.getcode(), url))
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
                    self._report_status("Downloading: {}KB".format(total_read / 1024))
                    zip_file.write(chunk)
            return file_path
        except IOError:
            raise ActionHandlerException(10502, "Error creating file: {}".format(file_path))

    def _unzip_files(self, file_path):
        destination_folder = os.path.join(self._temp_file_location, self._application.name)
        logger.info("Unzipping {} into {}".format(file_path, destination_folder))
        try:
            with zipfile.ZipFile(file_path, "r") as zip_file_handle:
                zip_file_handle.extractall(destination_folder)
                return destination_folder
        except Exception as ex:
            logger.error(ex.message)
            raise ActionHandlerException(10503, "Error unzipping file")

    def _inner_path(self, unzip_path):
        paths = [os.path.join(unzip_path, path) for path in listdir(unzip_path) if isdir(os.path.join(unzip_path, path))]
        if len(paths) > 1:
            logger.error("Zip file expected one but contains the following folders: {}".format(','.join(paths)))
            raise ActionHandlerException(10504, "Zip file contains unexpected layout")
        inner_path = paths[0]
        logger.info("Found folder in zip: {}".format(inner_path))
        return inner_path

    def _move_files(self, temp_destination):
        try:
            source_folder = self._inner_path(temp_destination)
            dest_folder = os.path.join(self._base_path, 'Peachy', self._application.relitive_install_path)
            move(source_folder, dest_folder)
            return dest_folder
        except ActionHandlerException:
            raise
        except Exception as ex:
            logger.error(ex)
            raise ActionHandlerException(10505, "Cannot move folders into install folder")

    def _create_shortcut(self, installed_path):
        try:
            link = os.path.join(os.getenv('USERPROFILE'), 'Desktop', self._application.name + '.lnk')
            target_file = os.path.join(installed_path, self._application.executable_path)
            working_dir = installed_path
            icon_file = os.path.join(installed_path, self._application.icon)

            ShortCutter.create_shortcut(link, target_file, working_dir, icon_file)
            return link
        except Exception as ex:
            logger.error(ex)
            raise ActionHandlerException(10506, "Creating shortcut failed")

    def _save_install_config(self, application):
        path = self._get_file_config_path(application.id)
        with open(path, 'w') as install_file:
            install_file.write(application.get_json())

    def start(self):
        pythoncom.CoInitialize()
        self._report_status("Downloading")
        file_path = self._fetch_zip(self._application.download_location)
        self._report_status("Unpacking")
        temp_destination = self._unzip_files(file_path)
        self._report_status("Installing")
        installed_path = self._move_files(temp_destination)
        self._report_status("Creating Shortcuts")
        shortcut_path = self._create_shortcut(installed_path)
        self._report_status("Finalizing")
        application = Application(self._application.id, self._application.name, installed_path=installed_path, shortcut_path=shortcut_path, current_version=self._application.available_version)
        self._save_install_config(application)
