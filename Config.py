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
from RoadNetwork import RoadNetwork
from SocialNetwork import SocialNetwork


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

    # Returns the network objects
    def getNetworks(self, type):
        if type == "road":
            title = "Road Networks"
        elif type == "social":
            title = "Social Networks"
        else:
            raise Exception("ERROR: getNetworks() must have type 'road' or 'social'")

        instances = {}
        # Loops through all networks
        for network in self.settings[title]:
            kwargs = {}
            # Loops through all data in each network
            for dataKey in self.settings[title][network]:
                dataValue = self.settings[title][network][dataKey]
                # If the value is set, use it to create the instance
                if dataValue != f"[{dataKey}]":
                    kwargs[dataKey] = dataValue
            if type == "road":
                instances[network] = RoadNetwork(network, **kwargs)
            elif type == "social":
                instances[network] = SocialNetwork(network, **kwargs)
        return instances

    def isComplete(self, type, network):
        if type == "road":
            type = "Road Networks"
        elif type == "social":
            type = "Social Networks"
        else:
            raise Exception("ERROR: isComplete() must have type 'road' or 'social'")
        for dataKey in self.settings[type][network]:
            dataValue = self.settings[type][network][dataKey]
            # If the value is set, use it to create the instance
            if dataValue == f"[{dataKey}]":
                return False
        return True

    # Return networks that have all files and those files exist
    def getCompleteNetworks(self):
        networks = {"Social Networks": [],
                    "Road Networks": []}

        # Road networks
        keys = self.getNetworks("road").keys()
        for i in keys:
            if self.isComplete("road", i):
                networks["Road Networks"].append(i)

        # Social networks
        keys = self.getNetworks("social").keys()
        for k in keys:
            if self.isComplete("social", k):
                networks["Social Networks"].append(k)
        return networks
