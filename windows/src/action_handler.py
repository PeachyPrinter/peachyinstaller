import threading
import os
import logging

from application_install import InstallApplication
from application_remove import RemoveApplication
from action_base import ActionHandlerException, ActionHandler

logger = logging.getLogger('peachy')


class AsyncActionHandler(threading.Thread, ActionHandler):
    def __init__(self, action, application, base_install_path, status_callback=None, complete_callback=None):
        threading.Thread.__init__(self)
        self._action = action
        self._application = application
        self._base_path = base_install_path
        self._status_callback = status_callback
        self._complete_callback = complete_callback
        self._report_status("Initializing")

    def run(self):
        try:
            if self._action == 'remove':
                RemoveApplication(self._application, status_callback=self._status_callback).start()
            elif self._action == 'upgrade':
                RemoveApplication(self._application, status_callback=self._status_callback).start()
                InstallApplication(self._application, self._base_path, status_callback=self._status_callback).start()
            elif self._action == 'install':
                InstallApplication(self._application, self._base_path, status_callback=self._status_callback).start()
            else:
                raise Exception("Action unsupported")
            self._report_status("Complete")
            self._report_complete(True, "Success")
        except ActionHandlerException as ex:
            self._report_status("Failed")
            self._report_complete(False, ex.message)
        except Exception as ex:
            logger.error(ex)
            raise
