import csv
import math
import threading
from os.path import exists


# =====================================================================================================================
#
#   Authors: Halie Eckert, Gavin Hulvey, Sydney Zuelzke
#   Date: 11/3/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       RoadNetwork.py is the class object for road networks.
#
# =====================================================================================================================
from PyQt5 import QtGui
from PyQt5.QtGui import QFont


class RoadNetwork:
    def __init__(self, name, edgeFile=None, nodeFile=None, POIFile=None, **kwargs):
        self.__name = name
        self.__edges = {}
        self.__nodes = {}
        self.__POIs = {}
        self.__flattenedData = [[], []]
        self.__flattenedPOIs = [[], [], []]
        self.__plotInstance = None
        # Create threads for loading files asynchronously
        threads = [threading.Thread(target=lambda: self.loadEdges(edgeFile)),
                   threading.Thread(target=lambda: self.loadNodes(nodeFile)),
                   threading.Thread(target=lambda: self.loadPOIs(POIFile))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.flattenData()
        self.flattenPOIs()

    # Reads edge file from path.
    # dict = {
    #    "edge_id": [start_id, end_id, weight],
    # }
    # noinspection PyShadowingBuiltins
    def loadEdges(self, path=None):
        if path is not None and exists(path):
            with open(path, 'r') as csvFile:
                reader = csv.reader(csvFile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    edge_id = row[0]
                    start_id = row[1]
                    end_id = row[2]
                    weight = row[3]
                    if edge_id in self.__edges:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        self.__edges[edge_id] = [start_id, end_id, weight]
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
            with open(path, 'r') as csvFile:
                reader = csv.reader(csvFile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    node_id = row[0]
                    lat = row[1]
                    lon = row[2]
                    if node_id in self.__nodes:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        self.__nodes[node_id] = [lat, lon]
        else:
            self.__nodes = None

    # Reads POI file from path.
    # dict = {
    #    "poi_id": [poi_category, lat_pos, lon_pos],
    # }
    # noinspection PyShadowingBuiltins
    def loadPOIs(self, path=None):
        if path is not None and exists(path):
            with open(path, 'r') as csvFile:
                reader = csv.reader(csvFile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    poi_id = row[0]
                    poi_category = row[1]
                    lat_pos = row[2]
                    lon_pos = row[3]
                    if poi_id in self.__POIs:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        self.__POIs[poi_id] = [poi_category, lat_pos, lon_pos]
        else:
            self.__POIs = None

    def flattenPOIs(self):
        if self.__POIs is not None:
            self.__flattenedPOIs[0] = [f"{i[0]}.png" for i in list(self.__POIs.values())]
            self.__flattenedPOIs[1] = [float(i[1]) for i in list(self.__POIs.values())]
            self.__flattenedPOIs[2] = [float(i[2]) for i in list(self.__POIs.values())]

    # Parses the edge data into instantly plottable lists. For example, lat is [startLat, endLat, None, startLat...]
    # This also chunks the data for faster processing and dedicates x number of threads to storing that data
    def flattenData(self):
        if self.__edges is not None and self.__nodes is not None:
            threads = []
            # Used to calculate amount of data in a chunk/thread
            threadCount = 10
            total = len(self.__edges)
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
        self.__flattenedData[0] = self.__flattenedData[0] + lat
        self.__flattenedData[1] = self.__flattenedData[1] + lon

    # Visualize the data
    def visualize(self, inst):
        # TODO: Figure out something about symbols for different places
        self.__plotInstance = inst.plot(self.__flattenedData[0], self.__flattenedData[1], connect='pairs', pen='black')
        inst.plot(self.__flattenedPOIs[1], self.__flattenedPOIs[2], pen=None, symbol='x',
                  symbolSize=2, symbolPen=(171, 145, 0, 20), symbolBrush=(171, 145, 0, 50))
