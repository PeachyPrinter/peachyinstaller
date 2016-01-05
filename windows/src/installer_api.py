import urllib2
import json


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


class InstallerAPI(InstallerAPIBase):
    supported_configuration_versions = [0, ]
    def __init__(self, config_url="http://www.github.com/peachyprinter/peachyinstaller/config.json"):
        self._config_url = config_url

    def _check_config(self, config):
        if "version" in config:
            if config["version"] not in self.supported_configuration_versions:
                return (False, 10304,  "Configuration version too new installer upgrade required")
        else:
            return (False, 10303, "Config is not valid")

    def initialize(self):
        result = urllib2.urlopen(self._config_url)
        if result.getcode() != 200:
            return (False, 10301, 'Connection unavailable')
        try:
            data = result.read()
            config = json.loads(data)
            result, error, message = self._check_config(config)
            if result is True:
                self._config = config
            else:
                return (False, error, message)
        except Exception as ex:
            print ex
            return(False, 10302, 'Data File Corrupt or damaged')
