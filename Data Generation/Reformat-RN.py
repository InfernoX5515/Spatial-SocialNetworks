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
            poi_dict["category"] = row[1]
            poi_dict["location"] = [float(row[2]), float(row[3])]
            poi_dict["keywords"] = []
            if poi_dict["category"] not in categories:
                categories += [poi_dict["category"]]
                poi_dict["category"] = len(categories) - 1
            else:
                poi_dict["category"] = categories.index(poi_dict["category"])
            with open(f"../Datasets/RoadNetworks/California/POIs/{poi_id}.json", "w") as f:
                json.dump(poi_dict, f, indent=4)
    with open("../Datasets/RoadNetworks/California/POI_categories.csv", 'w', newline='') as catFile:
        writer = csv.writer(catFile, delimiter=',',)
        writer.writerow(["category_id", "category"])
        for x in range(0, len(categories)):
            writer.writerow([x, categories[x]])


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
    poi_keyword_dict = {}
    with open("../Datasets/RoadNetworks/California_old/california_poi_key.csv", 'r') as kfile:
        reader = csv.reader(kfile, delimiter=',', quotechar='|')
        for row in reader:
            poi_id = int(float(row[0]))
            keyword_id = int(float(row[1]))
            if poi_id in poi_keyword_dict.keys():
                poi_keyword_dict[poi_id].append(keyword_id)
            else:
                poi_keyword_dict[poi_id] = [keyword_id]
        for item in poi_keyword_dict:
            if os.path.exists(f"../Datasets/RoadNetworks/California/POIs/{item}.json"):
                with open(f"../Datasets/RoadNetworks/California/POIs/{item}.json", "r") as f:
                    data = json.load(f)
                    data["keywords"] = poi_keyword_dict[item]
                    f.close()
                with open(f"../Datasets/RoadNetworks/California/POIs/{item}.json", "w") as f:
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
print(LINE_UP, "Adding pois...")
pois()
print(LINE_UP, "Adding keywords...       ")
key()

print("Complete!")
