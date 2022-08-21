from ast import keyword
import csv
import math
import threading
from os.path import exists
from tkinter.tix import Select
from unittest import result
#from aem import con
from sklearn.cluster import KMeans
import networkx as nx
import sqlite3
from collections import Counter

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
        self.loadNetworkX()

    def loadNetworkX(self):
        self.cursor.execute("SELECT UserID FROM UserLocations WHERE SocialNetwork=?",(self.id,))
        rows = self.cursor.fetchall()
        for row in rows:
            self.networkX.add_node(row[0])
        self.cursor.execute('''SELECT TargetUser, DestinationUser FROM UserRelationships 
                                JOIN UserLocations UT ON UserRelationships.TargetUser = UT.UserID
                                JOIN UserLocations UD ON UserRelationships.DestinationUser = UD.UserID 
                                WHERE UT.SocialNetwork=? AND UT.SocialNetwork=?''',(self.id,self.id))
        rows = self.cursor.fetchall()
        for row in rows:
            self.networkX.add_edge(row[0],row[1],weight=1)

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

        return chunked


    def getIDByLoc(self, lat, lon):
        self.cursor.execute("SELECT UserID FROM UserLocations WHERE SocialNetwork=? AND Latitude=? AND Longitude=?",(self.id,lat,lon))
        result = self.cursor.fetchone()
        return result[0]

    # Returns size for cluster icons so that clusters that contain fewer nodes are smaller
    @staticmethod
    def sizeSort(refs):
        sizes = []
        refsSorted = refs.copy()
        refsSorted.sort()
        for x in refs:
            sizes += [((refsSorted.index(x) + 1) * (75 / len(refsSorted)))]
        return sizes

    def getSummaryClusters(self, n):
        n = int(n)
        if n < 1:
            n = 10
        # n_clusters is th number of nodes to plot
        kmeans = KMeans(n_clusters=int(n))
        chunkedData = self.getChunkedLocData()
        users = self.getUsers()
        kmeans.fit(chunkedData)
        # Scales the nodes according to population
        centers = kmeans.cluster_centers_
        # Get items in clusters and put it into dictionary {'clusterid': [userid, userid...], ...}
        clusterItems = {}
        for i in range(0, len(chunkedData)):
            label = kmeans.labels_[i]
            userid = users[i]
            if label in clusterItems:
                clusterItems[label].append(userid)
            else:
                clusterItems[label] = [userid]
        clusterStart = list(clusterItems.keys())
        popSize = []
        for x in clusterItems:
            if isinstance(clusterItems[x], list):
                popSize.append(len(clusterItems[x]))
        relations = [[], []]
        while len(clusterStart) != 1:
            start = clusterStart[0]
            for item in clusterStart:
                if clusterStart[0] is not item:
                    relations[0] += [centers[start][0], centers[item][0]]
                    relations[1] += [centers[start][1], centers[item][1]]
                    # for user in clusterItems[start]:
                    #    for user2 in clusterItems[start]:
                    #        print(f"    {user}")
            clusterStart.pop(0)
        ref = list(Counter(kmeans.labels_).values())
        sizes = self.sizeSort(ref)
        return centers, sizes, relations, popSize

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
        del results[query]
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
            self.cursor.execute('''SELECT UT.Latitude, UT.Longitude, UD.Latitude, UD.Longitude FROM UserRelationships 
                                    JOIN UserLocations UT ON UserRelationships.TargetUser = UT.UserID 
                                    JOIN UserLocations UD ON UserRelationships.DestinationUser = UD.UserID 
                                    WHERE UD.SocialNetwork=? AND UT.SocialNetwork=?''',(self.id, self.id))
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
