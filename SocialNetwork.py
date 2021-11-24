import pandas as pa

# =====================================================================================================================
#
#   Author: Halie Eckert
#   Date: 11/3/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       SocialNetwork.py is the class object for social networks.
#
# =====================================================================================================================


class SocialNetwork:
    def __init__(self):
        self.__loc = None
        self.__rel = None

    # Reads loc file from path
    def loadLoc(self, path):
        self.__loc = pa.read_csv(path, header=1)

    # Reads rel file from path
    def loadRel(self, path):
        self.__rel = pa.read_csv(path, header=1)
