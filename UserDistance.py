import csv
import csv
from os.path import exists
import networkx as nx
from functools import partial


def find_nearest(points, coord):
    dist = lambda s, key: (s[0] - points[key][0]) ** 2 + \
                           (s[1] - points[key][1]) ** 2
    return min(points, key=partial(dist, coord))
    

class UserDistance:
    def __init__(self):
        self.network = nx.Graph()
        self.__nodes = {}
        self.__loc = {}
        self.__keywords = {}
        self.relRemoved = 0

        #
        # INSTRUCTIONS:
        # Update below path names then run
        #
        self.loadRoadEdges(path="./Datasets/RoadNetworks/california_edge.csv")
        self.loadRoadNodes(path="./Datasets/RoadNetworks/california_node.csv")
        
        self.loadSocialLoc(path="./Datasets/SocialNetworks/gowalla_loc.csv")
        self.loadSocialKeywords(path="./Datasets/SocialNetworks/gowalla_keywords.csv")
        self.loadSocialRel(path="./Datasets/SocialNetworks/gowalla_rel.csv", name="./Datasets/SocialNetworks/gowalla_n_rel.csv")
        print(str(self.relRemoved) + ' relationships were removed as user(s) could not be found in location dataset')
        self.relRemoved = 0
        print('GOWALLA DONE')
        self.loadSocialLoc(path="./Datasets/SocialNetworks/foursquare_loc.csv")
        self.loadSocialKeywords(path="./Datasets/SocialNetworks/foursquare_keywords.csv")
        self.loadSocialRel(path="./Datasets/SocialNetworks/foursquare_rel.csv", name="./Datasets/SocialNetworks/foursquare_n_rel.csv")
        print(str(self.relRemoved) + ' relationships were removed as user(s) could not be found in location dataset')
        self.relRemoved = 0
        print('FOURSQUARE DONE')

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
    def loadSocialRel(self, path=None, name='out.csv'):
        if 1 == 1:
            dict = {}
            with open(path, 'r') as readObj, \
                    open(name, 'w', newline='') as writeObj:
                reader = csv.reader(readObj, delimiter=',', quotechar='|')
                writer = csv.writer(writeObj)
                
                # Add header to output file
                writer.writerow(['user_id','rel_user_id','weight','distance','keywords'])
                next(reader)
                for row in reader:
                    user_id = row[0]
                    rel_user_id = row[1]
                    weight = row[2]

                    # Ensure users are in loc datasets
                    if(self.__loc.get(user_id, 0) == 0):
                        self.relRemoved = self.relRemoved + 1
                        continue
                    if(self.__loc.get(rel_user_id, 0) == 0):
                        self.relRemoved = self.relRemoved + 1
                        continue

                    usrA = find_nearest(self.__nodes, (float(self.__loc[user_id][0][0]), float(self.__loc[user_id][0][1])))
                    usrB = find_nearest(self.__nodes, (float(self.__loc[rel_user_id][0][0]), float(self.__loc[rel_user_id][0][1])))
                    commonKeywords= len(set(self.__keywords[user_id]) & set(self.__keywords[rel_user_id]))
                    row.append(nx.dijkstra_path_length(self.network, source=float(usrA), target=float(usrB)))
                    row.append(commonKeywords)
                    writer.writerow(row)

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

    def loadSocialKeywords(self, path=None):
        if 1 == 1:
            dict = {}
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(reader)
                for row in reader:
                    user_id = row[0]
                    keyword = row[1]
                    if user_id in dict:
                        dict[user_id] = dict[user_id] + [keyword]
                    else:
                        dict[user_id] = [keyword]
            self.__keywords = dict
        else:
            self.__keywords = None


def main():
    test = UserDistance()

if __name__ == '__main__':
    main()
