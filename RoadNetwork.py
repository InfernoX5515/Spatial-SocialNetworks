import csv
import fnmatch
import json
import math
import os
import pickle
import random
import re
import stat
import threading
import time
from os.path import exists
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtGui import QFont
import networkx as nx
from functools import partial
import scipy

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


def find_nearest(points, coord):
    dist = lambda s, key: (float(s[0]) - float(points[key][0])) ** 2 + (float(s[1]) - float(points[key][1])) ** 2
    return min(points, key=partial(dist, coord))


# Stores road network vertex's information
class RNVertex:
    def __init__(self, id, loc=None, edges=None):
        self.id = id
        self.loc = loc
        self.edges = edges

        # If a value is not set, initialize empty
        if loc is None:
            self.loc = []
        else:
            self.loc = loc
        if edges is None:
            self.edges = []
        else:
            self.edges = edges


# Stores road network POI's information
class RNPOI:
    def __init__(self, id, category=None, loc=None, keywords=None):
        self.id = id
        self.category = category
        self.loc = loc
        self.keywords = keywords

        # If a value is not set, initialize empty
        if category is None:
            self.category = []
        else:
            self.category = category
        if loc is None:
            self.loc = []
        else:
            self.loc = loc
        if keywords is None:
            self.keywords = []
        else:
            self.keywords = keywords

    # Add a keyword to a POI
    def addKeyword(self, keywordID):
        if keywordID not in self.keywords:
            self.keywords += keywordID

    # Remove a keyword from the POI
    def removeKeyword(self, keywordID):
        self.keywords.remove(keywordID)


class RoadNetwork:
    def __init__(self, name, Path=None):
        self.name = name
        self.dir = Path
        self.POIkeywordDict = None
        self.POIs = None
        self.vertices = None

        if self.dir is not None:
            if not os.path.exists(self.dir):
                os.mkdir(self.dir)
            else:
                threads = [threading.Thread(target=self.loadPOIKeywords),
                           threading.Thread(target=self.loadPOICategories),
                           threading.Thread(target=self.loadVertices),
                           threading.Thread(target=self.loadPOIs)]

                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()

    # Reads POI keyword files for given road network
    def loadPOIKeywords(self):
        keywordFile = f"{self.dir}/POI_keywords.csv"
        keywords = {}

        if os.path.exists(keywordFile):
            with open(keywordFile, 'r') as f:
                reader = csv.reader(f, delimiter=',', quotechar='|')
                next(reader)

                for row in reader:
                    keywordID = row[0]
                    keyword = row[1]
                    if keywordID not in keywords:
                        keywords[keywordID] = keyword

        else:
            f = open(keywordFile, "x")
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["keyword_id", "keyword"])
            f.close()

            self.POIkeywordDict = {}

        self.POIkeywordDict = keywords

    # Reads keyword files for given road network
    def loadPOICategories(self):
        categoryFile = f"{self.dir}/POI_categories.csv"
        category = {}

        if os.path.exists(categoryFile):
            with open(categoryFile, 'r') as f:
                reader = csv.reader(f, delimiter=',', quotechar='|')
                next(reader)

                for row in reader:
                    keywordID = row[0]
                    keyword = row[1]
                    if keywordID not in category:
                        category[keywordID] = keyword

        else:
            f = open(categoryFile, "x")
            writer = csv.writer(f, delimiter=',')
            writer.writerow(["category_id", "category"])
            f.close()

            self.POIkeywordDict = {}

        self.POIkeywordDict = category

    # Spawns threads for reading vertex files and creates/reads a pickle if created
    def loadVertices(self):
        self.vertices = {}
        vertexDir = f"{self.dir}/Vertices"
        # self.vertices will be stored in a pickle (object) to load. This is faster than recomputing everything every
        # time.
        picklePath = f"{self.dir}/Vertices.pickle"
        recreatePickle = True

        if os.path.exists(vertexDir):

            # Index to store objects so that they are not recreated every time unnecessarily
            if os.path.exists(picklePath):
                verticesLastModified = time.ctime(os.stat(vertexDir)[stat.ST_MTIME])
                indexLastModified = time.ctime(os.stat(picklePath)[stat.ST_MTIME])

                if verticesLastModified < indexLastModified:
                    recreatePickle = False

            if recreatePickle:
                files = os.listdir(vertexDir)

                threadCount = 6
                threads = []
                total = len(files)
                start = 0
                end = math.floor(total / threadCount)

                for x in range(1, threadCount + 1):
                    if x == threadCount + 1:
                        end = total

                    threads += [threading.Thread(target=lambda s=start, e=end: self.loadVertexFiles(files[s:e]))]
                    start = end
                    end = math.floor(total / threadCount) * (x + 1)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                with open(picklePath, 'wb') as f:
                    pickle.dump(self.vertices, f, pickle.HIGHEST_PROTOCOL)

            else:
                with open(picklePath, 'rb') as f:
                    self.vertices = pickle.load(f)

        else:
            os.mkdir(vertexDir)

    # Actually reads the data from vertex files. Spawned in threads by loadVertices()
    def loadVertexFiles(self, files):
        vertexDir = f"{self.dir}/Vertices"

        for file in files:
            with open(f"{vertexDir}/{file}", "r") as f:
                data = json.load(f)

                if data['id'] not in self.vertices:
                    indexKey = f"~{data['id']}~l:{data['location']}~e:{data['edges']}"
                    self.vertices[indexKey] = RNVertex(data['id'], loc=data['location'], edges=data['edges'])

    # Spawns threads for reading poi files and creates/reads a pickle if created
    def loadPOIs(self):
        self.POIs = {}
        POIDir = f"{self.dir}/POIs"
        # self.POIs will be stored in a pickle (object) to load. This is faster than recomputing everything every time.
        picklePath = f"{self.dir}/POIs.pickle"
        recreatePickle = True

        if os.path.exists(POIDir):

            # Index to store objects so that they are not recreated every time unnecessarily
            if os.path.exists(picklePath):
                POIsLastModified = time.ctime(os.stat(POIDir)[stat.ST_MTIME])
                indexLastModified = time.ctime(os.stat(picklePath)[stat.ST_MTIME])

                if POIsLastModified < indexLastModified:
                    recreatePickle = False

            if recreatePickle:
                files = os.listdir(POIDir)

                threadCount = 6
                threads = []
                total = len(files)
                start = 0
                end = math.floor(total / threadCount)

                for x in range(1, threadCount + 1):
                    if x == threadCount + 1:
                        end = total

                    threads += [threading.Thread(target=lambda s=start, e=end: self.loadPOIFiles(files[s:e]))]
                    start = end
                    end = math.floor(total / threadCount) * (x + 1)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                with open(picklePath, 'wb') as f:
                    pickle.dump(self.POIs, f, pickle.HIGHEST_PROTOCOL)

            else:
                with open(picklePath, 'rb') as f:
                    self.POIs = pickle.load(f)

        else:
            os.mkdir(POIDir)

    # Actually reads the data from vertex files. Spawned in threads by loadVertices()
    def loadPOIFiles(self, files):
        POIDir = f"{self.dir}/POIs"

        for file in files:
            with open(f"{POIDir}/{file}", "r") as f:
                data = json.load(f)

                if data['id'] not in self.vertices:
                    indexKey = f"~{data['id']}~c:{data['category']}~l:{data['location']}~kw:{data['keywords']}"
                    self.POIs[indexKey] = RNPOI(data['id'], category=data['category'], loc=data['location'],
                                                keywords=data['keywords'])

    # Returns a vertex when given an index, i.e. the 0th vertex loaded
    def getVertexByIndex(self, index):
        return self.vertices[list(self.vertices.keys())[index]]

    # Returns a vertex when given the vertex id
    def getVertexById(self, id):
        matching = fnmatch.filter(list(self.vertices.keys()), f"~{id}~*")

        if len(matching) != 1:
            for vertex in matching:
                if self.vertices[vertex].id == id:
                    return self.vertices[vertex]
            # If there is no match, error
            raise Exception("There were more than one possible match for getVertexById() but no matches!")

        return matching[0]

    # Returns vertex(s) at a given location
    def getVertexByLoc(self, lat, lon):
        matching = fnmatch.filter(list(self.vertices.keys()), f"*~l:[[]{lat}, {lon}[]]~kw:*")

        vertices = []
        for match in matching:
            vertices += [self.vertices[match]]

        return vertices

    # Returns a list of all vertex's locations
    def getAllVertexLocs(self):
        indexes = '\n'.join(list(self.vertices.keys()))
        coords = re.findall(r"(?<=~l:\[)(.*)(?=]~kw:)", indexes)
        return coords

    # Returns a POI when given an index, i.e. the 0th POI loaded
    def getPOIByIndex(self, index):
        return self.POIs[list(self.POIs.keys())[index]]

    # Returns a POI when given the POI id
    def getPOIById(self, id):
        matching = fnmatch.filter(list(self.POIs.keys()), f"~{id}~*")

        if len(matching) != 1:
            for POI in matching:
                if self.POIs[POI].id == id:
                    return self.POIs[POI]
            # If there is no match, error
            raise Exception("There were more than one possible match for getPOIById() but no matches!")

        return matching[0]

    # Returns POI(s) at a given location
    def getPOIByLoc(self, lat, lon):
        matching = fnmatch.filter(list(self.POIs.keys()), f"*~l:[[]{lat}, {lon}[]]~kw:*")

        POIs = []
        for match in matching:
            POIs += [self.POIs[match]]

        return POIs

    # Returns a list of all POI's locations
    def getAllPOILocs(self):
        indexes = '\n'.join(list(self.POIs.keys()))
        coords = re.findall(r"(?<=~l:\[)(.*)(?=]~kw:)", indexes)
        return coords

    def getEdges(self):
        print(list(self.vertices.keys()))
        #indexes = '\n'.join(list(self.users.keys()))
        #coords = re.findall(r"(?<=~ll:\[)(.*)(?=]~kw:)", indexes)

    # Visualize the data
    # lat: [[startlat, endlat], [startlat,endlat]]
    def visualize(self, showEdges=True, POIInst=False):
        self.getEdges()
        #print(self.vertices)
        # Display edges
        #if showEdges:
            #self.edgeInst = graph.plot(self.__flattenedData[0], self.__flattenedData[1], connect='pairs',
            #                              pen='black')
        '''if POIInst is not None:
            random.seed()
            for category in self.__flattenedPOIs:
                r = random.randrange(0, 256)
                g = random.randrange(0, 256)
                b = random.randrange(0, 256)
                self.POIInst = POIInst.plot(self.__flattenedPOIs[category][0], self.__flattenedPOIs[category][1],
                                            pen=None, symbol='x', symbolSize=2, symbolPen=(r, g, b, 20),
                                            symbolBrush=(r, g, b, 50))'''

'''
class RoadNetwork:
    def __init__(self, name, edgeFile=None, nodeFile=None, POIFile=None, POIKeyFile=None, POIKeyMapFile=None, **kwargs):
        self.__name = name
        self.networkX = nx.Graph()
        self.__edges = {}
        self.__nodes = {}
        self.__POIs = {}
        self.__keywordMap = {}
        self.__keywords = {}
        self.__flattenedData = [[], []]
        self.__flattenedPOIs = {}
        self.edgeInst = None
        self.POIInst = None
        # Create threads for loading files asynchronously
        threads = [threading.Thread(target=lambda: self.loadEdges(edgeFile)),
                   threading.Thread(target=lambda: self.loadNodes(nodeFile)),
                   threading.Thread(target=lambda: self.loadPOIs(POIFile)),
                   threading.Thread(target=lambda: self.loadKeys(POIKeyFile, POIKeyMapFile))]
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
                        self.networkX.add_edge(float(start_id), float(end_id), weight=float(weight))
        else:
            self.__edges = None

    # Reads node file from path. This is super awful but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "node_id": [lat, lon]
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
                        self.networkX.add_node(float(node_id))
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

    # Reads keyword files from path.
    # keywordMap = {
    #    "keyword_id": "keyword",
    #    "keyword_id": "keyword"
    # }
    #
    # keywords = {
    #     "user_id": [keyword_id, keyword_id],
    #     "user_id": [keyword_id]
    # }
    # noinspection SpellCheckingInspection,PyShadowingBuiltins
    def loadKeys(self, kPath=None, mPath=None):
        if kPath is not None and mPath is not None and exists(kPath) and exists(mPath):
            keywords = {}
            poiKeywords = {}
            # Gets key map
            with open(mPath, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    keyword_id = row[0]
                    keyword = row[1]
                    if keyword_id in keywords:
                        raise Exception(f"Error: Duplicate value in {mPath}")
                    else:
                        keywords[keyword_id] = keyword
            # Gets user keywords
            with open(kPath, 'r') as kfile:
                reader = csv.reader(kfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user_id = row[0]
                    keyword_id = row[1]
                    if user_id in list(poiKeywords.keys()):
                        poiKeywords[user_id].append(keyword_id)
                    else:
                        poiKeywords[user_id] = [keyword_id]
            self.__keywordMap = keywords
            self.__keywords = poiKeywords
        else:
            self.__keywordMap = None
            self.__keywords = None

    def flattenPOIs(self):
        if self.__POIs is not None:
            for poi in list(self.__POIs.keys()):
                index = self.__POIs[poi]
                if index[0] not in list(self.__flattenedPOIs.keys()):
                    self.__flattenedPOIs[index[0]] = [[float(index[1])], [float(index[2])]]
                else:
                    self.__flattenedPOIs[index[0]][0] += [float(index[1])]
                    self.__flattenedPOIs[index[0]][1] += [float(index[2])]

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

    def nodeCount(self):
        return len(list(self.__nodes.keys()))

    def closestNode(self, lat, long):
        tree = scipy.spatial.KDTree(list(self.__nodes.values()))
        i = tree.query([lat, long])[1]
        # id = list(self.__nodes.keys())[i]
        return i

    def isAnEdge(self, startId, endId):
        arr = np.array(list(self.__edges.values()))
        coords = arr[:, 0:2].tolist()
        if [startId, endId] in coords:
            return float(coords.index([startId, endId]))
        if [endId, startId] in coords:
            return float(coords.index([endId, startId]))
        return None

    def getEdgeDistance(self, edgeId):
        return self.__edges[edgeId][2]

    def findNearest(self, user):
        return find_nearest(self.__nodes, (float(user[0][0]), float(user[0][1])))

    def realUserDistance(self, usrA, usrB):
        return nx.dijkstra_path_length(self.networkX, source=float(usrA), target=float(usrB))

    # Visualize the data
    def visualize(self, edgeInst=None, POIInst=None):
        if edgeInst is not None:
            self.edgeInst = edgeInst.plot(self.__flattenedData[0], self.__flattenedData[1], connect='pairs',
                                          pen='black')
        if POIInst is not None:
            random.seed()
            for category in self.__flattenedPOIs:
                r = random.randrange(0, 256)
                g = random.randrange(0, 256)
                b = random.randrange(0, 256)
                self.POIInst = POIInst.plot(self.__flattenedPOIs[category][0], self.__flattenedPOIs[category][1],
                                            pen=None, symbol='x', symbolSize=2, symbolPen=(r, g, b, 20),
                                            symbolBrush=(r, g, b, 50))
'''
