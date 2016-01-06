
class Application(object):
    def __init__(self, web_config, installed_config=None):
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