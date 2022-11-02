import csv
import json
import os.path


def nodes():
    with open("../Datasets/RoadNetworks/California_old/california_node.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            node_id = int(float(row[0]))
            node_dict = {}
            node_dict["id"] = node_id
            node_dict["location"] = [float(row[1]), float(row[2])]
            node_dict["edges"] = []
            with open(f"../Datasets/RoadNetworks/California/Vertices/{node_id}.json", "w") as f:
                json.dump(node_dict, f, indent=4)


def pois():
    with open("../Datasets/RoadNetworks/California_old/california_poi.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        categories = []
        for row in reader:
            poi_id = int(float(row[0]))
            poi_dict = {}
            poi_dict["id"] = poi_id
            poi_dict["category"] = int(row[1])
            poi_dict["location"] = [float(row[2]), float(row[3])]
            poi_dict["keywords"] = []
            poiKeysPath = "../Datasets/RoadNetworks/California/POI_keywords.csv"
            if not os.path.exists(poiKeysPath):
                with open("../Datasets/RoadNetworks/California/POI_keywords.csv", 'w') as catFile:
                    writer = csv.writer(catFile, delimiter=',',)
                    writer.writerow(["category_id", "category"])
                    writer.writerow([0, poi_dict["category"]])
                    categories += poi_dict["category"]
                    poi_dict["category"] = 0
            else:
                highestID = 0
                with open("../Datasets/RoadNetworks/California/POI_keywords.csv", 'r') as catFile:
                    r = csv.reader(csvfile, delimiter=',', quotechar='|')
                    next(r)
                    for row2 in reader:
                        highestID = row2[0]

            with open(f"../Datasets/RoadNetworks/California/POIs/{poi_id}.json", "w") as f:
                json.dump(poi_dict, f, indent=4)


def loc():
    data = []
    with open("../Datasets/SocialNetworks/Gowalla_old/gowalla_loc.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            user_id = int(float(row[0]))
            lat_pos = float(row[1])
            lon_pos = float(row[2])
            with open(f"../Datasets/SocialNetworks/Gowalla/Users/{user_id}.json", "r") as f:
                data = json.load(f)
            with open(f"../Datasets/SocialNetworks/Gowalla/Users/{user_id}.json", "w") as f:
                if (lat_pos, lon_pos) not in data["login locations"]:
                    data["login locations"] += [[lat_pos, lon_pos]]
                    json.dump(data, f, indent=4)


def key():
    data = []
    user_keyword_dict = {}
    with open("../Datasets/SocialNetworks/Gowalla_old/gowalla_key.csv", 'r') as kfile:
        reader = csv.reader(kfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            user_id = int(float(row[0]))
            keyword_id = int(float(row[1]))
            if user_id in user_keyword_dict.keys():
                user_keyword_dict[user_id].append(keyword_id)
            else:
                user_keyword_dict[user_id] = [keyword_id]
        for item in user_keyword_dict:
            with open(f"../Datasets/SocialNetworks/Gowalla/Users/{item}.json", "r") as f:
                data = json.load(f)
                data["keywords"] = user_keyword_dict[item]
                f.close()
            with open(f"../Datasets/SocialNetworks/Gowalla/Users/{item}.json", "w") as f:
                json.dump(data, f, indent=4)


def edge():
    data = []
    with open("../Datasets/RoadNetworks/California_old/california_edge.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        node_edge_dict = {}
        for row in reader:
            node_id = int(float(row[1]))
            edge_node_id = int(float(row[2]))
            if node_id not in node_edge_dict:
                node_edge_dict[node_id] = [edge_node_id]
            else:
                node_edge_dict[node_id] += [edge_node_id]

        for item in node_edge_dict:
            with open(f"../Datasets/RoadNetworks/California/Vertices/{item}.json", "r") as f:
                try:
                    data = json.load(f)
                    data["edges"] = node_edge_dict[item]
                except Exception as e:
                    print(e)
            with open(f"../Datasets/RoadNetworks/California/Vertices/{item}.json", "w") as f:
                json.dump(data, f, indent=4)


LINE_UP = '\033[1A'

print("Creating nodes...")
nodes()
print(LINE_UP, "Adding node edges...")
edge()
'''print(LINE_UP, "Adding user locations...")
loc()
print(LINE_UP, "Adding keywords...       ")
key()
'''
print("Complete!")
