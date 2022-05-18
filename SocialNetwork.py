from ast import keyword
import csv
import math
import threading
from os.path import exists
from tkinter.tix import Select
from unittest import result
from aem import con
import networkx as nx
import sqlite3

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
    def __init__(self, name, relFile=None, locFile=None, keyFile=None, keyMapFile=None, id=1, **kwargs):
        self.__name = name
        self.id = id
        self.networkX = nx.MultiGraph()
        self.connection = sqlite3.connect("dataset.db")
        self.cursor = self.connection.cursor()
        self.__rel = {}
        self.__loc = {}
        self.__flattenedRelData = [[], []]
        self.__flattenedLocData = [[], []]
        self.__chunkedLocData = []
        threads = [threading.Thread(target=lambda: self.loadRel(path=relFile)),
                   threading.Thread(target=lambda: self.loadLoc(path=locFile))]
    
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
        self.cursor.execute("SELECT Latitude, Longitude FROM UserLocations WHERE SocialNetwork=?",(self.id,))
        rows = self.cursor.fetchall()
        flat = [[],[]]
        for d in rows:
            flat[0].append(d[0])
            flat[1].append(d[1])
        return flat

    def getChunkedLocData(self):
        self.cursor.execute("SELECT Latitude, Longitude, UserID FROM UserLocations WHERE SocialNetwork=?",(self.id,))
        rows = self.cursor.fetchall()
        chunked = []
        for row in rows:
            temp = []
            temp.append(row[0])
            temp.append(row[1])
            chunked.append(temp)
        print(chunked)

        return chunked

    def IDByLoc(self):
        temp = {}
        for id in self.__loc:
            for loc in self.__loc[id]:
                temp[f'{loc}'] = id
        return temp

    def getIDByLoc(self, lat, lon):
        self.cursor.execute("SELECT UserID FROM UserLocations WHERE SocialNetwork=? AND Latitude=? AND Longitude=?",(self.id,lat,lon))
        result = self.cursor.fetchone()
        print(result)
        return result[0]
        #return self.IDByLoc[f"['{lat}', '{lon}']"]

    # Returns all keywords
    def getKeywords(self):
        self.cursor.execute("SELECT Keyword FROM Keywords")
        rows = self.cursor.fetchall()
        data = []
        for row in rows:
            data.append(row[0])
        return data

    def getIDByKeyword(self, keyword):
        self.cursor.execute("SELECT ID FROM Keywords WHERE Keyword=?",(keyword,))
        rows = self.cursor.fetchall()
        return rows[0][0]

    def getKeywordByID(self, id):
        self.cursor.execute("SELECT Keyword FROM Keywords WHERE ID=?",(id,))
        rows = self.cursor.fetchall()
        return rows[0][0]

    def getUsersWithKeywords(self, keywords):
        sql = ""
        for keyword in keywords:
            if sql != "":
                sql += " INTERSECT "
            sql += f"SELECT KeywordMap.UserID FROM KeywordMap JOIN UserLocations UL ON KeywordMap.UserID = UL.UserID WHERE KeywordID ={keyword} AND UL.SocialNetwork={self.id}"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        matches = []
        for row in rows:
            matches.append(row[0])
        return matches

    def getUsersWithKeyword(self, keyword):
        self.cursor.execute("SELECT KeywordMap.UserID FROM KeywordMap JOIN UserLocations UL ON KeywordMap.UserID = UL.UserID WHERE KeywordMap.KeywordID =? AND UL.SocialNetwork=?",(int(keyword),self.id))
        rows = self.cursor.fetchall()
        matches = []
        for row in rows:
            matches.append(row[0])
        return matches

    def getUser(self, userID):
        self.cursor.execute("SELECT Latitude, Longitude FROM UserLocations WHERE SocialNetwork=? AND UserID=?",(self.id,userID))
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append(row)
        return [userID, result]

    def getUserKeywords(self, userID):
        self.cursor.execute("SELECT KeywordID FROM KeywordMap WHERE UserID=?",(userID,))
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
        return result

    def usersCommonKeywords(self,query,k=1):
        queryKeys = self.getUserKeywords(query)
        results = {}
        for key in queryKeys:
            users = self.getUsersWithKeyword(key)
            for user in users:
                if user in results:
                    results[user] = results[user] + 1
                else:
                    results[user] = 1
        detalied = {}
        for key in results:
            if results[key] >= k:
                detalied[key] = results[key]
        return [key for (key, value) in results.items() if value >= k], detalied

    def getUsers(self):
        self.cursor.execute("SELECT UserID FROM UserLocations WHERE SocialNetwork=?",(self.id,))
        rows = self.cursor.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
        return result

    def userLoc(self, userID):
        self.cursor.execute("SELECT Latitude, Longitude FROM UserLocations WHERE UserID=? AND SocialNetwork=?",(userID, self.id))
        rows = self.cursor.fetchall()
        return rows

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
            self.cursor.execute("SELECT UT.Latitude, UT.Longitude, UD.Latitude, UD.Longitude FROM UserRelationships JOIN UserLocations UT ON UserRelationships.TargetUser = UT.UserID JOIN UserLocations UD ON UserRelationships.DestinationUser = UD.UserID WHERE UD.SocialNetwork=? AND UT.SocialNetwork=?",(self.id, self.id))
            rows = self.cursor.fetchall()
            flat = [[],[]]
            for row in rows:
                flat[0].append(row[0])
                flat[1].append(row[1])
                flat[0].append(row[2])
                flat[1].append(row[3])
            snInst.plot(flat[0], flat[1], connect='pairs', pen=(50, 50, 200, 10),
                        brush=(50, 50, 200, 100))
        if rnInst is not None:
            flat = self.getFlattenedLocData()
            rnInst.plot(flat[0], flat[1], pen=None, symbol='o', symbolSize=2,
                        symbolPen=(50, 50, 200, 25), symbolBrush=(50, 50, 200, 175))
