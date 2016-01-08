import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..',))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from application import Application

class TestHelpers(object):
    def get_sample_application_config(self):
        return {
            "id": 1,
            "name": {
                "en-us": "aa",
                },
            "version": "0.1.2",
            "location": "http://someurl",
            "install_path": "bb",
            "executable": "cc.exe",
            "install_type": "zip",
            "icon": "resources\\icon.ico"
        }

    def get_sample_web_config(self):
        return '{"version": 0, "applications":[%s]}' % json.dumps(self.get_sample_application_config())

    def get_sample_installed_config(self):
        return {
            "id": 1,
            "name": {
                "en-us": "aa",
                },
            "version": "0.1.1",
            "installed_path": "bb",
    }

    def get_sample_file_config(self):
        return '{"version": 0, "applications":[%s]}' % json.dumps(self.get_sample_installed_config())

    def get_application(self):
        return Application.from_configs(self.get_sample_application_config())
