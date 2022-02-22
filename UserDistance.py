import csv
from RoadNetwork import RoadNetwork
import csv
import math
import threading
from os.path import exists
# FIND A BETER REPLACEMENT
from dijkstar import Graph, find_path

from functools import partial

def find_nearest(points, coord):
    dist = lambda s, key: (s[0] - points[key][0]) ** 2 + \
                           (s[1] - points[key][1]) ** 2
    return min(points, key=partial(dist, coord))

class UserDistance:
    def __init__(self):
        self.g = Graph()
        self.__nodes = {}
        self.loadEdges(path="/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/RoadNetworks/california_edge.csv")
        self.loadNodes(path="/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/RoadNetworks/california_node.csv")
        #4227
        usrA = find_nearest(self.__nodes, (-122.430635, 37.774158))
        #32993
        usrB = find_nearest(self.__nodes, (-122.416664, 37.761966))
        print(find_path(self.g, usrA, usrB))

    # Reads edge file from path.
    # dict = {
    #    "edge_id": [start_id, end_id, weight],
    # }
    # noinspection PyShadowingBuiltins
    def loadEdges(self, path=None):
        
        if path is not None and exists(path):
            dict = {}
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    edge_id = row[0]
                    start_id = row[1]
                    end_id = row[2]
                    weight = row[3]
                    if edge_id in dict:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        self.g.add_edge(float(start_id), float(end_id), float(weight))

    # Reads node file from path. This is super awful but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "node_id":
    #    [
    #       [lat, lon],
    #       [lat, lon]
    #    ]
    # }
    # noinspection PyShadowingBuiltins
    def loadNodes(self, path=None):
        if path is not None and exists(path):
            dict = {}
            # noinspection SpellCheckingInspection
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    node_id = row[0]
                    lat = row[1]
                    lon = row[2]
                    if node_id in dict:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        dict[node_id] = (float(lat), float(lon))
            self.__nodes = dict
        else:
            self.__nodes = None



