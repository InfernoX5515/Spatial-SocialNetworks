import csv
import math
import threading
from os.path import exists


# =====================================================================================================================
#
#   Author: Halie Eckert
#   Date: 11/3/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       RoadNetwork.py is the class object for road networks.
#
# =====================================================================================================================


# TODO: Customize time messages more
class RoadNetwork:
    # TODO: Add protection against loading file that does not exist
    def __init__(self, name=None, edges=None, nodes=None):
        self.__name = name
        self.__edges = {}
        self.__nodes = {}
        self.__normalizedData = [[], []]
        threads = []
        if edges is not None and exists(edges):
            threads.append(threading.Thread(target=lambda: self.loadEdges(path=edges)))
        if nodes is not None and exists(nodes):
            threads.append(threading.Thread(target=lambda: self.loadNodes(path=nodes)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.normalizeData()
        self.__visual = None

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
                        dict[edge_id] = [start_id, end_id, weight]
            self.__edges = dict
        else:
            self.__edges = None

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
                        dict[node_id] = [lat, lon]
            self.__nodes = dict
        else:
            self.__nodes = None

    # Parses the edge data into instantly plottable lists. For example, lat is [startLat, endLat, None, startLat...]
    # This also chunks the data for faster processing and dedicates x number of threads to storing that data
    def normalizeData(self):
        if self.__edges is not None and self.__nodes is not None:
            threads = []
            total = len(self.__edges)
            threadCount = 10
            start = 0
            end = math.floor(total / threadCount)
            for x in range(1, threadCount + 1):
                if x == threadCount + 1:
                    end = total
                threads.append(threading.Thread(target=lambda s=start, e=end, y=x: self.parseDataChunk(s, e * y)))
                start = end * x
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

    # Parses a single chunk of data and adds it to the master list
    def parseDataChunk(self, start, end):
        lat = []
        lon = []
        edgeList = list(self.__edges)
        for x in range(start, end):
            y = edgeList[x]
            node = self.__edges[y][0]
            edge = self.__edges[y][1]
            startLat = float(self.__nodes[node][0])
            startLon = float(self.__nodes[node][1])
            endLat = float(self.__nodes[edge][0])
            endLon = float(self.__nodes[edge][1])
            lat = lat + [startLat, endLat]
            lon = lon + [startLon, endLon]
        self.__normalizedData[0] = self.__normalizedData[0] + lat
        self.__normalizedData[1] = self.__normalizedData[1] + lon

    # Visualize the data
    def visualize(self, inst):
        self.__visual = inst.plot(self.__normalizedData[0], self.__normalizedData[1], connect='pairs', pen='black')
