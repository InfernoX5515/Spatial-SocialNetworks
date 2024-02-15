import json
from os.path import exists

# =====================================================================================================================
#
#   Authors: Halie Eckert, Gavin Hulvey, Sydney Zuelzke
#   Date: 11/9/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       Config.py is the class object for the project config. It currently handles storing road networks and file
#       locations
#
# =====================================================================================================================


class Config:
    def __init__(self):
        self.settings = self.defSettings()
        self.loadSettings()

    # Defines the base config settings
    @staticmethod
    def defSettings():
        settings = {
            "Road Networks": {},
            "Social Networks": {}
        }
        return settings

    # Updates a setting to a value
    def update(self, setting, value):
        self.settings[setting] = value
        with open("config.json", 'w') as f:
            f.write(json.dumps(self.settings, indent=4, sort_keys=True))

    # Loads the settings if the file exists and if not, create it
    def loadSettings(self):
        if exists("config.json"):
            with open("config.json", 'r') as f:
                self.settings = json.load(f)
        else:
            with open("config.json", 'w') as f:
                f.write(json.dumps(self.settings, indent=4, sort_keys=True))

    # Returns the loaded settings
    def getSetting(self, setting):
        return self.settings[setting]
