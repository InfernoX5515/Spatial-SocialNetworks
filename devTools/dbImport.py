import csv
from os.path import exists
import sqlite3
from turtle import distance

class dbImport:
    def __init__(self):
        self.connection = sqlite3.connect("../dataset.db")
        self.cursor = self.connection.cursor()
        #self.loadRoadNodes(path="../Datasets/RoadNetworks/california_node.csv")
        #self.loadRoadEdges(path="../Datasets/RoadNetworks/california_edge.csv")
        #self.loadLocations(path="../Datasets/SocialNetworks/Foursquare/foursquare_loc.csv")
        #self.loadUserRelations(path="../Datasets/SocialNetworks/Foursquare/foursquare_rel.csv")
        #self.loadKeywords(path="../Datasets/SocialNetworks/Gowalla/gowalla_key_map.csv")
        self.loadKeywordMap(path="../Datasets/SocialNetworks/Foursquare/foursquare_key.csv")
        self.connection.commit()

    def loadRoadNodes(self, path=None):
        if path is not None and exists(path):
            dict = {}
            # noinspection SpellCheckingInspection
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                ID = 1
                for row in reader:
                    node_id = row[0]
                    lat = row[1]
                    lon = row[2]
                    if node_id in dict:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        self.cursor.execute("INSERT INTO Nodes (ID, Longitude, Latitude, RoadNetwork) VALUES (?, ?, ?, 1)", (ID, int(lon)+1, int(lat)+1))
                        #print(f"INSERT INTO Nodes (ID, Longitude, Latitude, RoadNetwork) VALUES ({ID}, {float(lon)}, {float(lat)}, 1)")
                        dict[node_id] = (float(lat), float(lon))
                        ID = ID + 1
            self.__nodes = dict
        else:
            self.__nodes = None
    
    def loadRoadEdges(self, path=None):
        
        if path is not None and exists(path):
            dict = {}
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                ID = 1
                for row in reader:
                    edge_id = row[0]
                    start_id = row[1]
                    end_id = row[2]
                    weight = row[3]
                    if edge_id in dict:
                        raise Exception(f"Error: Duplicate value in {path}")
                    else:
                        #{ID}, {start_id}, {end_id}, {weight}
                        self.cursor.execute(f"INSERT INTO EDGES (ID, StartNode, EndNode, Weight) VALUES (?,?,?,?)",(ID, int(float(start_id)) + 1, int(float(end_id)) + 1, float(weight)))
                        ID = ID + 1

    def loadLocations(self, path=None):
        
        if path is not None and exists(path):
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user_id = row[0]
                    lat_pos = row[1]
                    lon_pos = row[2]
                    #196561 - Foursquare offset
                    self.cursor.execute(f"INSERT INTO UserLocations (UserID, Longitude, Latitude, SocialNetwork) VALUES (?,?,?,?)",(int(float(user_id))+196561, float(lon_pos), float(lat_pos), 2))
    
    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False
    
    def loadUserRelations(self, path=None):
        if path is not None and exists(path):
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                ID=10271
                for row in reader:
                    user_id = row[0]
                    rel_user_id = row[1]
                    weight = row[2]
                    distance = row[3]
                    #10271 - Foursquare offset
                    if self.is_float(user_id) and self.is_float(rel_user_id):
                        self.cursor.execute(f"INSERT INTO UserRelationships (ID, TargetUser, DestinationUser, Weight, Distance) VALUES (?,?,?,?,?)",( ID, int(float(user_id))+196561, int(float(rel_user_id))+196561, float(weight), float(distance)))
                        ID = ID + 1

    def loadKeywords(self, path=None):
        if path is not None and exists(path):
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    id = row[0]
                    keyword = row[1]
                    self.cursor.execute(f"INSERT INTO Keywords (ID, Keyword) VALUES (?,?)",(int(float(id)), keyword))


    def loadKeywordMap(self, path=None):
        if path is not None and exists(path):
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user = row[0]
                    keyword = row[1]
                    self.cursor.execute(f"INSERT INTO KeywordMap (UserID, KeywordID) VALUES (?,?)",(int(float(user))+196561, keyword))



def main():
    test = dbImport()

if __name__ == '__main__':
    main()