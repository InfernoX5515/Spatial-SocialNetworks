import csv
import json


def first():
    with open("Datasets/SocialNetworks/Gowalla_old/gowalla_user.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            user_id = int(float(row[0]))
            user_dict = {}
            user_dict["id"] = user_id
            user_dict["username"] = row[1]
            user_dict["name"] = row[2]
            user_dict["email"] = row[3]
            user_dict["birthdate"] = row[4]
            user_dict["phone"] = row[5]
            user_dict["keywords"] = []
            user_dict["login locations"] = []
            user_dict["relationships"] = []
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{user_id}.json", "w") as f:
                json.dump(user_dict, f, indent=4)


def loc():
    data = []
    with open("Datasets/SocialNetworks/Gowalla_old/gowalla_loc.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        for row in reader:
            user_id = int(float(row[0]))
            lat_pos = float(row[1])
            lon_pos = float(row[2])
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{user_id}.json", "r") as f:
                data = json.load(f)
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{user_id}.json", "w") as f:
                if (lat_pos, lon_pos) not in data["login locations"]:
                    data["login locations"] += [[lat_pos, lon_pos]]
                    json.dump(data, f, indent=4)


def key():
    data = []
    user_keyword_dict = {}
    with open("Datasets/SocialNetworks/Gowalla_old/gowalla_key.csv", 'r') as kfile:
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
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{item}.json", "r") as f:
                data = json.load(f)
                data["keywords"] = user_keyword_dict[item]
                f.close()
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{item}.json", "w") as f:
                json.dump(data, f, indent=4)


def rel():
    data = []
    with open("Datasets/SocialNetworks/Gowalla_old/gowalla_rel.csv", 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)
        user_rel_weight_dict = {}
        for row in reader:
            user_id = int(float(row[0]))
            rel_user_id = int(float(row[1]))
            weight = float(row[2])
            if user_id in user_rel_weight_dict.keys():
                user_rel_weight_dict[user_id].append([rel_user_id, weight])
            else:
                user_rel_weight_dict[user_id] = [[rel_user_id, weight]]

        for item in user_rel_weight_dict:
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{item}.json", "r") as f:
                try:
                    data = json.load(f)
                    data["relationships"] = [[user_rel_weight_dict[item][0], user_rel_weight_dict[item][1]]]
                    # data["relationships"] = ["Adsf"]
                except Exception as e:
                    print(e)
            with open(f"Datasets/SocialNetworks/Gowalla/Users/{item}.json", "w") as f:
                json.dump(data, f, indent=4)


LINE_UP = '\033[1A'

print("Creating users...")
first()
print(LINE_UP, "Adding user locations...")
loc()
print(LINE_UP, "Adding keywords...       ")
key()
print(LINE_UP, "Adding user relations...")
rel()
print("Complete!")
