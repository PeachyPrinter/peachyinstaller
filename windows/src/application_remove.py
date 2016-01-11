import threading
import os
from os import listdir
from os.path import isdir
import logging



from application import Application
from action_handler import ActionHandler, ActionHandlerException

logger = logging.getLogger('peachy')

class RemoveApplication(threading.Thread, ActionHandler):
    def __init__(self, application, status_callback=None, complete_callback=None):
        threading.Thread.__init__(self)
        self._application = application
        self._status_callback = status_callback
        self._complete_callback = complete_callback
        self._report_status("Initializing")

    def run(self):
        try:
            self._report_status("Removing")
            self._report_complete(True, "Success")
        except ActionHandlerException as ex:
            self._report_complete(False, ex.message)
        except Exception as ex:
            logger.error(ex)
            raise

