import csv
import datetime
import fnmatch
import json
import math
import multiprocessing
import os.path
import pickle
import re
import stat
import threading
import time
from os.path import exists
import networkx as nx

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


# Stores social network user information
class SNUser:
    def __init__(self, id, loginLocs=None, keywords=None, relations=None, username=None, name=None, email=None,
                 birthdate=None, phone=None):
        self.id = id
        self.username = username
        self.name = name
        self.email = email
        self.birthdate = birthdate
        self.phone = phone
        if loginLocs is None:
            self.loginLocs = []
        else:
            self.loginLocs = loginLocs
        if keywords is None:
            self.keywords = []
        else:
            self.keywords = keywords
        if relations is None:
            self.relations = {}
        else:
            self.relations = relations

    def addLoginLoc(self, lat, lon):
        if (lat, lon) not in self.loginLocs:
            self.loginLocs += (lat, lon)

    def removeLoginLoc(self, lat, lon):
        self.loginLocs.remove((lat, lon))

    def addKeyword(self, keywordID):
        if keywordID not in self.keywords:
            self.keywords += keywordID

    def removeKeyword(self, keywordID):
        self.keywords.remove(keywordID)

    def addRelation(self, userID, weight):
        if userID not in self.relations:
            self.relations[userID] = weight

    def removeRelation(self, userID):
        del self.relations[userID]


class SocialNetwork:
    def __init__(self, name, dir=None):
        self.name = name
        self.dir = dir
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

        self.keywordDict = None
        self.users = None

        threads = [threading.Thread(target=self.loadKeywords),
                   threading.Thread(target=self.loadUsers)]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    # Reads keyword files for given social network
    def loadKeywords(self):
        keywordFile = f"{self.dir}/keywords.csv"
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

            self.keywordDict = {}

        self.keywordDict = keywords

    def loadUsers(self):
        self.users = {}
        userDir = f"{self.dir}/Users"
        # self.users will be stored in a pickle (object) to load. This is faster than recomputing everything every time.
        picklePath = f"{self.dir}/Users.pickle"
        recreatePickle = True

        if os.path.exists(userDir):

            # Index to store objects so that they are not recreated every time unnecessarily
            if os.path.exists(picklePath):
                usersLastModified = time.ctime(os.stat(userDir)[stat.ST_MTIME])
                indexLastModified = time.ctime(os.stat(picklePath)[stat.ST_MTIME])

                if usersLastModified < indexLastModified:
                    recreatePickle = False

            if recreatePickle:
                files = os.listdir(userDir)

                threadCount = 6
                threads = []
                total = len(files)
                start = 0
                end = math.floor(total / threadCount)

                for x in range(1, threadCount + 1):
                    if x == threadCount + 1:
                        end = total

                    threads += [threading.Thread(target=lambda s=start, e=end: self.loadUserFiles(files[s:e]))]
                    start = end
                    end = math.floor(total / threadCount) * (x + 1)

                for thread in threads:
                    thread.start()

                for thread in threads:
                    thread.join()

                with open(picklePath, 'wb') as f:
                    pickle.dump(self.users, f, pickle.HIGHEST_PROTOCOL)

            else:
                with open(picklePath, 'rb') as f:
                    self.users = pickle.load(f)

        else:
            os.mkdir(userDir)

    def loadUserFiles(self, files):
        userDir = f"{self.dir}/Users"

        for file in files:
            with open(f"{userDir}/{file}", "r") as f:
                data = json.load(f)

                if data['id'] not in self.users:
                    indexKey = f"~{data['id']}~ll:{data['login locations']}~kw:{data['keywords']}"
                    self.users[indexKey] = SNUser(data['id'], loginLocs=data['login locations'],
                                                  keywords=data['keywords'], relations=data['relationships'],
                                                  username=data['username'], name=data['name'], email=data['email'],
                                                  birthdate=data['birthdate'], phone=data['phone'])

    def getUserByIndex(self, index):
        return self.users[list(self.users.keys())[index]]

    def getUserById(self, id):
        matching = fnmatch.filter(list(self.users.keys()), f"~{id}~*")

        if len(matching) != 1:
            for user in matching:
                if self.users[user].id == id:
                    return self.users[user]
            # If there is no match, error
            raise Exception("There were more than one possible match for getUserId() but no matches!")

        return self.users[matching[0]]

    def getUserIndexStr(self, id):
        matching = fnmatch.filter(list(self.users.keys()), f"~{id}~*")

        if len(matching) != 1:
            for user in matching:
                if self.users[user].id == id:
                    return self.users[user]
            # If there is no match, error
            raise Exception("There were more than one possible match for getUserId() but no matches!")

        return matching[0]

    def getUserByLoc(self, lat, lon):
        matching = fnmatch.filter(list(self.users.keys()), f"*~ll:[[]*[[]{lat}, {lon}[]]*[]]~kw:*")

        users = []
        for match in matching:
            users += [self.users[match]]

        return users

    def getAllLocs(self):
        indexes = '\n'.join(list(self.users.keys()))
        coords = re.findall(r"(?<=~ll:\[)(.*)(?=]~kw:)", indexes)
        return coords

'''class SocialNetwork:
    def __init__(self, name, relFile=None, locFile=None, keyFile=None, keyMapFile=None, userDataFile=None, **kwargs):
        ~~self.__name = name
        self.networkX = nx.MultiGraph()
        self.__rel = {}
        self.__loc = {}
        ~self.__userData = {}
        ~self.__keywordMap = {}
        ~self.__keywordMapReverse = {}
        ~self.__keywords = {}
        self.__flattenedRelData = [[], []]
        self.__flattenedLocData = [[], []]
        self.__chunkedLocData = []
        ~threads = [~threading.Thread(target=lambda: self.loadRel(path=relFile)),
                   ~threading.Thread(target=lambda: self.loadLoc(path=locFile)),
                   ~~threading.Thread(target=lambda: self.loadUser(path=userDataFile)),
                   ~~threading.Thread(target=lambda: self.loadKey(kPath=keyFile, mPath=keyMapFile))]

        ~for thread in threads:
            ~thread.start()
        ~for thread in threads:
            ~thread.join()
        self.IDByLoc = self.IDByLoc()
        self.flattenRelData()
        self.flattenLocData()
        self.chunkLocData()


    # Read in user attributes from the given path
    # "USER ID" {
    #   "username": value,
    #   "name": value,
    #   "email": value,
    #   "birthdate": value,
    #   "phone": value
    # }
    ~def loadUser(self, path=None):
        ~if path is not None and exists(path):
            ~dict = {}
            ~with open(path, 'r') as csvfile:
                ~reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                ~next(reader)
                ~for row in reader:
                    ~user_id = row[0]
                    ~user_dict = {}
                    ~user_dict["username"] = row[1]
                    ~user_dict["name"] = row[2]
                    ~user_dict["email"] = row[3]
                    ~user_dict["birthdate"] = row[4]
                    ~user_dict["phone"] = row[5]
                    ~dict[user_id] = user_dict
            ~self.__userData = dict
        ~else:
            ~self.__userData = None

    def getUserAttributes(self, user_id):
        return self.__userData[user_id]

    # Reads rel file from path. This is super awful, but it's the fastest way to do things. This is what it returns:
    # dict = {
    #    "user_id":
    #    [
    #       [rel_user_id, weight],
    #       [rel_user_id, weight]
    #    ]
    # }
    # noinspection PyShadowingBuiltins
    ~def loadRel(self, path=None):
        ~if path is not None and exists(path):
            ~dict = {}
            ~with open(path, 'r') as csvfile:
                ~reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                ~next(reader)
                ~for row in reader:
                    ~user_id = row[0]
                    ~rel_user_id = row[1]
                    ~weight = row[2]
                    ~if user_id in dict:
                        ~dict[user_id] = dict[user_id] + [[rel_user_id, weight]]
                    ~else:
                        ~dict[user_id] = [[rel_user_id, weight]]
                    self.networkX.add_edge(float(user_id), float(rel_user_id), weight=1)
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
                    self.networkX.add_node(float(user_id))
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
    ~~def loadKey(self, kPath=None, mPath=None):
        ~~if kPath is not None and mPath is not None and exists(kPath) and exists(mPath):
            ~~keywords = {}
            ~~keywordsReverse = {}
            ~~userKeywords = {}
            # Gets key map
            ~~with open(mPath, 'r') as csvfile:
                ~~reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                ~~next(reader)
                ~~for row in reader:
                    ~~keyword_id = row[0]
                    ~~keyword = row[1]
                    ~~if keyword_id in keywords:
                        ~~raise Exception(f"Error: Duplicate value in {mPath}")
                    ~~else:
                        ~~keywords[keyword_id] = keyword
                        ~~keywordsReverse[keyword] = keyword_id
            # Gets user keywords
            ~~with open(kPath, 'r') as kfile:
                ~~reader = csv.reader(kfile, delimiter=',', quotechar='|')
                ~~next(reader)
                ~~for row in reader:
                    ~~user_id = str(float(row[0]))
                    ~~keyword_id = row[1]
                    ~~if user_id in list(userKeywords.keys()):
                        ~~userKeywords[user_id].append(keyword_id)
                    ~~else:
                        ~~userKeywords[user_id] = [keyword_id]
            ~~self.__keywordMap = keywords
            ~~self.__keywordMapReverse = keywordsReverse
            ~~self.__keywords = userKeywords
        ~~else:
            ~~self.__keywordMap = None
            ~~self.__keywordMapReverse = None
            ~~self.__keywords = None

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

    # Returns all keywords
    def getKeywords(self):
        return list(self.__keywordMap.values())

    def getIDByKeyword(self, keyword):
        return str(self.__keywordMapReverse[keyword])

    def getKeywordByID(self, id):
        return str(self.__keywordMap[id])

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

    def userLoc(self, userID):
        return self.__loc[userID]

    def numberOfHops(self, start, end):
        hops = 0
        try:
            hops = nx.dijkstra_path_length(self.networkX, float(start), float(end))
        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            hops = -1
        #return self.networkX.number_of_edges(float(start), float(end))
        return hops

    def commonRelations(self, target, users):
        result = []
        for user in users:
            if self.networkX.has_edge(user,target):
                result.append(user)
        return result

    # Visualize the data
    def visualize(self, snInst=None, rnInst=None):
        if snInst is not None:
            snInst.plot(self.__flattenedRelData[0], self.__flattenedRelData[1], connect='pairs', pen=(50, 50, 200, 10),
                        brush=(50, 50, 200, 100))
        if rnInst is not None:
            rnInst.plot(self.__flattenedLocData[0], self.__flattenedLocData[1], pen=None, symbol='o', symbolSize=2,
                        symbolPen=(50, 50, 200, 25), symbolBrush=(50, 50, 200, 175))
'''