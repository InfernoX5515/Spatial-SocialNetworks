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
#       SocialNetwork.py is the class object for social networks.
#
# =====================================================================================================================


class SocialNetwork:
    def __init__(self, name, relFile=None, locFile=None, keyFile=None, keyMapFile=None, **kwargs):
        self.__name = name
        self.__rel = {}
        self.__loc = {}
        self.__keywordMap = {}
        self.__keywords = {}
        self.__flattenedRelData = [[], []]
        self.__flattenedLocData = [[], []]
        self.__chunkedLocData = []
        threads = [threading.Thread(target=lambda: self.loadRel(path=relFile)),
                   threading.Thread(target=lambda: self.loadLoc(path=locFile)),
                   threading.Thread(target=lambda: self.loadKey(kPath=keyFile, mPath=keyMapFile))]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.IDByLoc = self.IDByLoc()
        self.flattenRelData()
        self.flattenLocData()
        self.chunkLocData()

    # Reads rel file from path. This is super awful, but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "user_id":
    #    [
    #       [rel_user_id, weight],
    #       [rel_user_id, weight]
    #    ]
    # }
    # noinspection PyShadowingBuiltins
    def loadRel(self, path=None):
        if path is not None and exists(path):
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
        if path is not None and exists(path):
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
    def loadKey(self, kPath=None, mPath=None):
        if kPath is not None and mPath is not None and exists(kPath) and exists(mPath):
            keywords = {}
            userKeywords = {}
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
                    user_id = str(float(row[0]))
                    keyword_id = row[1]
                    if user_id in list(userKeywords.keys()):
                        userKeywords[user_id].append(keyword_id)
                    else:
                        userKeywords[user_id] = [keyword_id]
            self.__keywordMap = keywords
            self.__keywords = userKeywords
        else:
            self.__keywordMap = None
            self.__keywords = None

    # Parses the rel data into instantly plottable lists. For example, lat is [startLat, endLat, None, startLat...]
    # This also chunks the data for faster processing and dedicates x number of threads to storing that data.
    def flattenRelData(self):
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
        self.__flattenedRelData[0] = self.__flattenedRelData[0] + lat
        self.__flattenedRelData[1] = self.__flattenedRelData[1] + lon

    # Parses the loc data into instantly plottable lists. For example, lat is [lat, lon, lat, lon...]
    # This also chunks the data for faster processing and dedicates x number of threads to storing that data.
    def flattenLocData(self):
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
        self.__flattenedLocData[0] = self.__flattenedLocData[0] + lat
        self.__flattenedLocData[1] = self.__flattenedLocData[1] + lon

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

    def getFlattenedLocData(self):
        return self.__flattenedLocData

    def getChunkedLocData(self):
        return self.__chunkedLocData

    def IDByLoc(self):
        temp = {}
        for id in self.__loc:
            for loc in self.__loc[id]:
                temp[f'{loc}'] = id
        return temp

    def getIDByLoc(self, lat, lon):
        return self.IDByLoc[f"['{lat}', '{lon}']"]

    # TODO: Change this to return keyword not keyword_id when keyword is generated
    # Returns all keywords
    def getKeywords(self):
        return list(self.__keywordMap.keys())

    def getUsersWithKeywords(self, keywords):
        matches = []
        for user in list(self.__loc.keys()):
            if keywords:
                match = True
                for keyword in keywords:
                    if user not in self.__keywords or keyword not in self.__keywords[user]:
                        match = False
                        break
                if not match:
                    continue
                matches.append(user)
            else:
                if user not in self.__keywords:
                    matches.append(user)
        return matches

    def getUser(self, userID):
        return [userID, self.__loc[userID]]

    def getUserKeywords(self, userID):
        if userID in self.__keywords:
            return self.__keywords[userID]
        else:
            return []

    def getUsers(self):
        return list(self.__loc.keys())

    # Visualize the data
    def visualize(self, snInst=None, rnInst=None):
        if snInst is not None:
            snInst.plot(self.__flattenedRelData[0], self.__flattenedRelData[1], connect='pairs', pen=(50, 50, 200, 10),
                        brush=(50, 50, 200, 100))
        if rnInst is not None:
            rnInst.plot(self.__flattenedLocData[0], self.__flattenedLocData[1], pen=None, symbol='o', symbolSize=2,
                        symbolPen=(50, 50, 200, 25), symbolBrush=(50, 50, 200, 175))
