import csv
import math
import threading
from os.path import exists
import numpy as np


# =====================================================================================================================
#
#   Authors: Halie Eckert, Gavin Hulvey, Sydney Zuelzke
#   Date: 11/3/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       SocialNetwork.py is the class object for social networks.
#
# =====================================================================================================================


class SocialNetwork:
    def __init__(self, name=None, rel=None, loc=None):
        self.__name = name
        self.__rel = {}
        self.__loc = {}
        self.__normalizedRelData = [[], []]
        self.__normalizedLocData = [[], []]
        self.__chunkedLocData = []
        threads = []
        if rel is not None and exists(rel):
            threads.append(threading.Thread(target=lambda: self.loadRel(path=rel)))
        if loc is not None and exists(loc):
            threads.append(threading.Thread(target=lambda: self.loadLoc(path=loc)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.normalizeRelData()
        self.normalizeLocData()
        self.chunkLocData()
        self.__visual = None

    # Reads rel file from path. This is super awful but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "user_id":
    #    [
    #       [rel_user_id, weight],
    #       [rel_user_id, weight]
    #    ]
    # }
    # noinspection PyShadowingBuiltins
    def loadRel(self, path=None):
        if path is not None:
            dict = {}
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user_id = row[0]
                    rel_user_id = row[1]
                    weight = row[2]
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
    def loadLoc(self, path=None):
        if path is not None:
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

    # Parses the rel data into instantly plottable lists. For example, lat is [startLat, endLat, None, startLat...]
    # This also chunks the data for faster processing and dedicates x number of threads to storing that data.
    def normalizeRelData(self):
        if self.__rel is not None and self.__loc is not None:
            threads = []
            total = len(self.__rel)
            threadCount = 10
            start = 0
            end = math.floor(total / threadCount)
            for x in range(1, threadCount + 1):
                if x == threadCount + 1:
                    end = total
                threads.append(threading.Thread(target=lambda s=start, e=end, y=x: self.parseRelDataChunk(s, e * y)))
                start = end * x
            for thread in threads:
                thread.start()
            # for thread in threads:
            #    thread.join()

    # Parses a single chunk of data and adds it to the master list
    # noinspection SpellCheckingInspection
    def parseRelDataChunk(self, start, end):
        # TODO: Include weight
        lat = []
        lon = []
        relList = list(self.__rel)
        for x in range(start, end):
            y = relList[x]
            rels = self.__rel[y]
            if y in self.__loc:
                locs = self.__loc[y]
                for z in locs:
                    startLat = float(z[0])
                    startLon = float(z[1])
                    for a in rels:
                        if a[0] in self.__loc:
                            for b in range(0, len(self.__loc[a[0]])):
                                endLat = float(self.__loc[a[0]][b][0])
                                endLon = float(self.__loc[a[0]][b][1])
                                lat = lat + [startLat, endLat]
                                lon = lon + [startLon, endLon]
        self.__normalizedRelData[0] = self.__normalizedRelData[0] + lat
        self.__normalizedRelData[1] = self.__normalizedRelData[1] + lon

    # Parses the loc data into instantly plottable lists. For example, lat is [lat, lon, lat, lon...]
    # This also chunks the data for faster processing and dedicates x number of threads to storing that data.
    def normalizeLocData(self):
        if self.__loc is not None:
            threads = []
            total = len(self.__loc)
            threadCount = 10
            start = 0
            end = math.floor(total / threadCount)
            for x in range(1, threadCount + 1):
                if x == threadCount + 1:
                    end = total
                threads.append(
                    threading.Thread(target=lambda s=start, e=end, y=x: self.parseLocDataChunk(s, e * y)))
                start = end * x
            for thread in threads:
                thread.start()
            # for thread in threads:
            #    thread.join()

    # Parses a single chunk of data and adds it to the master list
    # noinspection SpellCheckingInspection
    def parseLocDataChunk(self, start, end):
        lat = []
        lon = []
        locList = list(self.__loc)
        for x in range(start, end):
            y = locList[x]
            locs = self.__loc[y]
            for z in range(0, len(locs)):
                lat = lat + [float(locs[z][0])]
                lon = lon + [float(locs[z][1])]
        self.__normalizedLocData[0] = self.__normalizedLocData[0] + lat
        self.__normalizedLocData[1] = self.__normalizedLocData[1] + lon

    # Chunks coords from [[lat, lat, lat...],[lon, lon, lon...]] to [[lat, lon], [lat lon]...]
    def chunkLocData(self):
        if self.__loc is not None:
            threads = []
            total = len(self.__loc)
            threadCount = 10
            start = 0
            end = math.floor(total / threadCount)
            for x in range(1, threadCount + 1):
                if x == threadCount + 1:
                    end = total
                threads.append(
                    threading.Thread(target=lambda s=start, e=end, y=x: self.parseChunkLocChunk(s, e * y)))
                start = end * x
            for thread in threads:
                thread.start()
            # for thread in threads:
            #    thread.join()

    # Parses a single chunk of data and adds it to the master list
    # noinspection SpellCheckingInspection
    def parseChunkLocChunk(self, start, end):
        coords = []
        locList = list(self.__loc)
        for x in range(start, end):
            y = locList[x]
            locs = self.__loc[y]
            for z in range(0, len(locs)):
                coords = coords + [[float(locs[z][0]), float(locs[z][1])]]
        self.__chunkedLocData = self.__chunkedLocData + coords

    def getNormalizedLocData(self):
        return self.__normalizedLocData

    def getChunkedLocData(self):
        return self.__chunkedLocData

    # Visualize the data
    def visualize(self, snInst, rnInst):
        snInst.plot(self.__normalizedRelData[0], self.__normalizedRelData[1], connect='pairs', pen=(50, 50, 200, 10), brush=(50, 50, 200, 100))
        rnInst.plot(self.__normalizedLocData[0], self.__normalizedLocData[1], pen=None, symbol='o', symbolSize=2,
                    symbolPen=(50, 50, 200, 25), symbolBrush=(50, 50, 200, 175))
