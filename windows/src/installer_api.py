import urllib2

class InstallerAPIBase(object):
    def check_version(self):
        raise NotImplementedException("This is not implemented at this time.")

    def get_items(self):
        raise NotImplementedException("This is not implemented at this time.")

    def get_item(self, id):
        raise NotImplementedException("This is not implemented at this time.")

    def process(self, id, install=False, remove=False, status_callback=None, complete_callback=None):
        raise NotImplementedException("This is not implemented at this time.")

    def initialize(self):
        raise NotImplementedException("This is not implemented at this time.")

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
    def __init__(self, config_url="http://www.github.com/peachyprinter/peachyinstaller/config.json"):
        self._config_url = config_url

    def initialize(self):
        result = urllib2.urlopen(self._config_url)
        if result.getcode() != 200:
            return (False, 10301, 'Connection unavailable')
        try:
            data = result.read()
            config = json.loads(data)
            # if self.check_config(config):
            #     self._config = config
            # else:
            #     return (False, 10302, 'Data File Corrupt or damaged')
        except:
            return(False, 10302, 'Data File Corrupt or damaged')