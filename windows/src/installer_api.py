import urllib2
import json
import os

from application import Application

import logging
logger = logging.getLogger('peachy')


class InstallerAPIBase(object):
    def check_version(self):
        raise NotImplementedError("This is not implemented at this time.")

    def get_items(self):
        raise NotImplementedError("This is not implemented at this time.")

    def get_item(self, id):
        raise NotImplementedError("This is not implemented at this time.")

    def process(self, id, install=False, remove=False, status_callback=None, complete_callback=None):
        raise NotImplementedError("This is not implemented at this time.")

    def initialize(self):
        raise NotImplementedError("This is not implemented at this time.")

class ConfigException(Exception):
    def __init__(self, error_code, message):
        super(ConfigException, self).__init__(message)
        logger.error("{} - {}".format(error_code, message))
        self.error_code = error_code


class InstallerAPI(InstallerAPIBase):
    supported_configuration_versions = [0, ]


    def __init__(self, config_url="https://raw.githubusercontent.com/PeachyPrinter/peachyinstaller/master/config.json"):
        logger.info("Fetching configuration from {}".format(config_url))
        self._config_url = config_url
        self._applications = []
        logger.info("Starting API")

    def _check_web_config(self, config):
        if "version" in config:
            if config["version"] not in self.supported_configuration_versions:
                raise ConfigException(10304,  "Configuration version too new installer upgrade required")
        else:
            raise ConfigException(10303, "Config is not valid")

    def _get_web_config(self):
        result = urllib2.urlopen(self._config_url)
        if result.getcode() != 200:
            raise ConfigException(10301, 'Connection unavailable')
        try:
            data = result.read()
            config = json.loads(data)
            self._check_web_config(config)
            return config
        except ConfigException:
            raise
        except Exception as ex:
            print ex
            raise ConfigException(10302, 'Web data File Corrupt or damaged')

    def _get_file_config_path(self):
        profile = os.getenv('USERPROFILE')
        company_name = "Peachy"
        app_name = 'PeachyInstaller'
        return os.path.join(profile, 'AppData', 'Local', company_name, app_name, 'installed.json')

    def _get_file_config(self,):
        file_path = self._get_file_config_path()
        try:
            if not os.path.exists(file_path):
                return None
            with open(file_path, 'r') as a_file:
                data = a_file.read()
                return json.loads(data)
        except IOError:
            raise ConfigException(10401, "Install File Inaccessable")
        except ValueError:
            raise ConfigException(10402, "Install File Corrupt or Damaged")

    def initialize(self):
        try:
            web_config = self._get_web_config()
            file_config = self._get_file_config()
            if file_config:
                file_config_ids = [app['id'] for app in file_config['applications']]
            else:
                file_config_ids = []

            for web_app in web_config['applications']:
                if web_app['id'] in file_config_ids:
                    file_app = [app for app in file_config['applications'] if app['id'] == web_app['id']][0]
                    self._applications.append(Application(web_app, file_app))
                else:
                    self._applications.append(Application(web_app))
        except ConfigException as cfgex:
            return (False, cfgex.error_code, cfgex.message)
        return (True, "0", "Success")

    def get_items(self):
        return self._applications

    def get_item(self, id):
        return [app for app in self._applications if app.id == id][0]
