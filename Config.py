import json
from os.path import exists

# =====================================================================================================================
#
#   Authors: Halie Eckert, Gavin Hulvey, Sydney Zuelzke
#   Date: 11/9/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       Config.py is the class object for the project config.
#
# =====================================================================================================================


class Config:
    def __init__(self):
        if exists("config.json"):
            self.loadSettings()
        else:
            self.settings = self.defSettings()
            f = open("config.json", 'w')
            f.write(json.dumps(self.settings, indent=4, sort_keys=True))
            f.close()

    @staticmethod
    def defSettings():
        settings = {
            "Road Networks": {},
            "Social Networks": {}
        }
        return settings

    def update(self, setting, value):
        self.settings[setting] = value
        f = open("config.json", 'w')
        f.write(json.dumps(self.settings, indent=4, sort_keys=True))
        f.close()

    def loadSettings(self):
        f = open("config.json", 'r')
        self.settings = json.load(f)
        f.close()

    def getSetting(self, setting):
        return self.settings[setting]
