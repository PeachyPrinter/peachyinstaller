import os
import logging

logger = logging.getLogger('peachy')

class ActionHandlerException(Exception):
    def __init__(self, error_code, message):
        super(ActionHandlerException, self).__init__(message)
        logger.error("{} - {}".format(error_code, message))
        self.error_code = error_code


class ActionHandler(object):
    def _report_status(self, message):
        logger.info(message)
        if self._status_callback:
            self._status_callback(message)

    def _report_complete(self, success, message):
        logger.info(message)
        if self._complete_callback:
            self._complete_callback(success, message)

    def _get_file_config_path(self, app_id):
        profile = os.getenv('USERPROFILE')
        company_name = "Peachy"
        app_name = 'PeachyInstaller'
        return os.path.join(profile, 'AppData', 'Local', company_name, app_name, 'app-{}.json'.format(app_id))