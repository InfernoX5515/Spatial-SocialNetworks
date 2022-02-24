import csv
from RoadNetwork import RoadNetwork
import csv
import math
import threading
from os.path import exists
# FIND A BETER REPLACEMENT
from dijkstar import Graph, find_path
import networkx as nx  # importing networkx package

from functools import partial

def find_nearest(points, coord):
    dist = lambda s, key: (s[0] - points[key][0]) ** 2 + \
                           (s[1] - points[key][1]) ** 2
    return min(points, key=partial(dist, coord))
    

class UserDistance:
    def __init__(self):
        self.network = nx.Graph()
        self.__nodes = {}
        self.__rel = {}
        self.__loc = {}
        self.loadRoadEdges(path="/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/RoadNetworks/california_edge.csv")
        self.loadRoadNodes(path="/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/RoadNetworks/california_node.csv")
        self.loadSocialLoc(path="/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/gowalla_loc.csv")
        self.loadSocialRel(path="/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/gowalla_rel.csv")

        #print(self.__loc['58257.0'][0][0])

        #4227
        usrA = find_nearest(self.__nodes, (-122.430635, 37.774158))
        #32993
        usrB = find_nearest(self.__nodes, (-122.416664, 37.761966))
        #print(nx.dijkstra_path_length(self.network, source=float(0.0), target=float(99.0)))

    # Reads edge file from path.
    # dict = {
    #    "edge_id": [start_id, end_id, weight],
    # }
    # noinspection PyShadowingBuiltins
    def loadRoadEdges(self, path=None):
        
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
                        self.network.add_edge(float(start_id), float(end_id), weight=float(weight))

    # Reads node file from path. This is super awful but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "node_id":
    #    [
    #       [lat, lon],
    #       [lat, lon]
    #    ]
    # }
    # noinspection PyShadowingBuiltins
    def loadRoadNodes(self, path=None):
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
                        self.network.add_node(float(node_id))
                        dict[node_id] = (float(lat), float(lon))
            self.__nodes = dict
        else:
            self.__nodes = None

    # Reads rel file from path. This is super awful but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "user_id":
    #    [
    #       [rel_user_id, weight],
    #       [rel_user_id, weight]
    #    ]
    # }
    # noinspection PyShadowingBuiltins
    def loadSocialRel(self, path=None):
        if 1 == 1:
            dict = {}
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user_id = row[0]
                    rel_user_id = row[1]
                    weight = row[2]
                    usrA = find_nearest(self.__nodes, (float(self.__loc[user_id][0][0]), float(self.__loc[user_id][0][1])))
                    usrB = find_nearest(self.__nodes, (float(self.__loc[rel_user_id][0][0]), float(self.__loc[rel_user_id][0][1])))
                    print(nx.dijkstra_path_length(self.network, source=float(usrA), target=float(usrB)))

                    if user_id in dict:
                        dict[user_id] = dict[user_id] + [[rel_user_id, weight]]
                    else:
                        dict[user_id] = [[rel_user_id, weight]]
            self.__rel = dict
        else:
            self.__rel = None

    # Reads loc file from path.
    # dict = {
    #    "user_id":
    #    [
    #       [lat_pos, lon_pos],
    #       [lat_pos, lon_pos]
    #    ]
    # }
    # noinspection SpellCheckingInspection,PyShadowingBuiltins
    def loadSocialLoc(self, path=None):
        if 1 == 1:
            dict = {}
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user_id = row[0]
                    lat_pos = row[1]
                    lon_pos = row[2]
                    if user_id in dict:
                        dict[user_id] = dict[user_id] + [lat_pos, lon_pos]
                    else:
                        dict[user_id] = [[lat_pos, lon_pos]]
            self.__loc = dict
        else:
            self.__loc = None



