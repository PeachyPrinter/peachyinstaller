import json


class Application(object):
    def __init__(self,
                 id,
                 name,
                 available_version=None,
                 download_location=None,
                 relitive_install_path=None,
                 executable_path=None,
                 installed_path=None,
                 icon=None,
                 current_version=None,
                 shortcut_path=None):
        self.id = id
        self.name = name
        self.available_version = available_version
        self.download_location = download_location
        self.relitive_install_path = relitive_install_path
        self.executable_path = executable_path
        self.installed_path = installed_path
        self.icon = icon
        self.current_version = current_version
        self.shortcut_path = shortcut_path

    @classmethod
    def from_configs(cls, web_config, installed_config=None):
        if installed_config and installed_config['id'] != web_config['id']:
            raise Exception("Unexpected error processing config")
        id = web_config['id']
        name = web_config['name']['en-us']
        available_version = web_config['version']
        download_location = web_config['location']
        relitive_install_path = web_config['install_path']
        icon = web_config['icon']
        executable_path = web_config['executable']
        if installed_config:
            installed_path = installed_config['installed_path']
            current_version = installed_config['version']
            shortcut_path = installed_config['shortcut_path']
        else:
            installed_path = None
            current_version = None
            shortcut_path = None
        return cls(id, name, available_version, download_location, relitive_install_path, executable_path, installed_path, icon, current_version, shortcut_path)

    def get_json(self):
        this = {
            "id": self.id,
            "name": {
                    "en-us": self.name,
                    },
            "available_version": self.available_version,
            "download_location": self.download_location,
            "relitive_install_path": self.relitive_install_path,
            "executable_path": self.executable_path,
            "installed_path": self.installed_path,
            "icon": self.icon,
            "current_version": self.current_version,
            "shortcut_path": self.shortcut_path,
        }
        for (key, value) in this.items():
            if value is None:
                del this[key]
        return json.dumps(this)

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
            self.installed_path == other.installed_path and
            self.icon == other.icon and
            self.current_version == other.current_version and
            self.shortcut_path == other.shortcut_path
            )
