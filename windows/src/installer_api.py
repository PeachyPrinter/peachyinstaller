import urllib2
import json
import os


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


class InstallerAPIStub(InstallerAPIBase):
    product = [
            {'id': 1, 'name': "Peachy Printer (64bit)*", 'installed': True},
            {'id': 2, 'name': "Peachy Printer (32bit)", 'installed': False},
            {'id': 3, 'name': "Peachy Scanner (64bit)*", 'installed': False},
            {'id': 4, 'name': "Peachy Scanner (32bit)", 'installed': False},
            ]

    def check_version(self):
        pass

    def get_items(self):
        return self.product

    def get_item(self, id):
        name = [dicti['name'] for dicti in self.product if dicti['id'] == id][0]
        return name

    def process(self, id, install=False, remove=False, status_callback=None, complete_callback=None):
        status_callback(id, "Woot")
        complete_callback(id, True)

    def initialize(self):
        return True

class ConfigException(Exception):
    def __init__(self, error_code, message):
        super(ConfigException, self).__init__(message)
        self.error_code = error_code

class Application(object):
    def __init__(self, web_config, installed_config = None):
        if installed_config and installed_config['id'] != web_config['id']:
            raise Exception("Unexpected error processing config")
        self.id = web_config['id']
        self.name = web_config['name']['en-us']
        self.available_version = web_config['version']
        self.download_location = web_config['location']
        self.relitive_install_path = web_config['install_path']
        self.executable_path = web_config['executable']
        if installed_config:
            self.full_installed_path = installed_config['installed_path']
            self.current_version = installed_config['version']
        else:
            self.full_installed_path = None
            self.current_version = None

    @property
    def actions(self):
        if self.current_version is not None:
            if self.current_version == self.available_version:
                return ['remove']
            else:
                return ['remove', 'upgrade']
        else:
            return ['install']

    def __eq__(self, other):
        return (
            self.id == other.id and
            self.name == other.name and
            self.available_version == other.available_version and
            self.download_location == other.download_location and
            self.relitive_install_path == other.relitive_install_path and
            self.executable_path == other.executable_path and
            self.full_installed_path == other.full_installed_path and
            self.current_version == other.current_version
            )


class InstallerAPI(InstallerAPIBase):
    supported_configuration_versions = [0, ]

    def __init__(self, config_url="http://www.github.com/peachyprinter/peachyinstaller/config.json"):
        self._config_url = config_url

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
        except Exception:
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
                a_file.read()
                return None
        except IOError:
            raise ConfigException(10401, "Install File Inaccessable")

    def initialize(self):
        try:
            self._web_config = self._get_web_config()
            self._file_config = self._get_file_config()
        except ConfigException as cfgex:
            return (False, cfgex.error_code, cfgex.message)
        return (True, "0", "Success")

    def get_items(self):
        return [Application(app) for app in self._web_config['applications']]
