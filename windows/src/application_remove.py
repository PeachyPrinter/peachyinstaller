from os import remove
from os.path import isfile, isdir
from shutil import rmtree
import logging

from action_handler import ActionHandler, ActionHandlerException

logger = logging.getLogger('peachy')

class RemoveApplication(ActionHandler):
    def __init__(self, application, status_callback=None):
        self._application = application
        self._status_callback = status_callback
        self._report_status("Initializing")

    def start(self):
        self._report_status("Removing Application")
        if isdir(self._application.installed_path):
            rmtree(self._application.installed_path)
        else:
            self._report_status("Application Not Found")
        self._report_status("Removing Shortcut")
        if isfile(self._application.shortcut_path):
            remove(self._application.shortcut_path)
        else:
            self._report_status("Shortcut Not Found")
        self._report_status("Cleaning up install history")
        path = self._get_file_config_path(self._application.id)
        if isfile(path):
            remove(path)
        else:
            self._report_status("Install history missing")
        self._report_status("Finished Removing Files")
