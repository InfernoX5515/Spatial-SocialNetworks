from SocialNetwork import SocialNetwork
from os.path import exists
import os
import json
from pyvis.network import Network
import networkx as nx
import pyqtgraph as pg
from sys import argv, exit
from pyqtgraph.Qt.QtGui import QApplication
from decimal import Decimal

def main(): 
    app = QApplication(argv)

    dirname = os.path.dirname(__file__)

    query_user = "5352.0"
    number_of_hops = 3

    graph = pg.plot(title="Road Network")

    gowalla_rel = "/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/Gowalla/gowalla_rel.csv"
    gowalla_loc = "/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/Gowalla/gowalla_loc.csv"
    gowalla_key = "/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/Gowalla/gowalla_key.csv"
    gowalla_key_map = "/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/Gowalla/gowalla_key_map.csv"
    gowalla_user = "/Users/gavinhulvey/Documents/GitHub/Spatial-SocialNetworks/Datasets/SocialNetworks/Gowalla/gowalla_user.csv"

    socialNetwork = SocialNetwork('Gowalla',gowalla_rel, gowalla_loc, gowalla_key, gowalla_key_map, gowalla_user)
    query_keywords = socialNetwork.getUserKeywords(query_user)
    query_rels_raw = socialNetwork.getUserRel(query_user)
    query_rels = []
    for r in query_rels_raw:
        query_rels.append(r[0])
    pre_tree = gen_tree(query_user, query_keywords, query_rels, 0.5, 0.5, socialNetwork, number_of_hops)
    tree = prune_tree(pre_tree, 0.2)


    result_users, pass_users = tree_users(tree)

    
    all_users = set(result_users) | set(pass_users)
    x = []
    y = []
    x_pass = []
    y_pass = []
    network = nx.Graph()
    for u in result_users:
        network.add_node(u, physics=False, label=str(u), color='blue', size=15)
        user_location = socialNetwork.userLoc(u)
        x.append(float(user_location[0][0]))
        y.append(float(user_location[0][1]))
    graph.plot(x, y, pen=None, symbol='o', symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
    for u in pass_users:
        user_location = socialNetwork.userLoc(u)
        x_pass.append(float(user_location[0][0]))
        y_pass.append(float(user_location[0][1]))
        network.add_node(u, physics=False, label=str(u), color='gray', size=15)
    graph.plot(x_pass, y_pass, pen=None, symbol='o', symbolPen=(0, 0, 255), symbolBrush=(0, 0, 255, 125))

    query_loc = socialNetwork.userLoc(query_user)[0]

    graph.plot([float(query_loc[0])], [float(query_loc[1])], pen=None, symbol='star', symbolSize=30, symbolPen=(0,255, 0), symbolBrush=(0, 255, 0, 255))

    network.add_node(query_user, physics=False, label=str(query_user), color='green', size=15, shape='star')

    for u in all_users:
        rels = socialNetwork.getUserRel(u)
        rel_users = []
        for r in rels:
            rel_users.append(r[0])
        relations = set(rel_users) & set(all_users)
        for r in relations:
            network.add_edge(u, r, color='black')

    nt = Network('100%', '100%')
    nt.from_nx(network)
    nt.save_graph('community-query.html')


    

    #rels = socialNetwork.getUserRel(query_user)
    #for r in rels:
    #    temp = { r[0]: [] }
    #    tree[query_user].append(temp)

    # Serializing json
    json_object = json.dumps(tree, indent=4)
    
    # Writing to sample.json
    with open("tree.json", "w") as outfile:
        outfile.write(json_object)

    

    print('DONE!')
    app.quit()
    exit(app.exec_())

def gen_tree(user, query_keywords, query_rels, g, h, network, hops, parents=[], distance=0, i=0):
    # Do not repeat nodes
    parents.append(user)

    rels = network.getUserRel(user)
    rel_users = []
    for r in rels:
        rel_users.append(r[0])
    rel_score = len(set(query_rels) & set(rel_users)) / len(set(query_rels) | set(rel_users))

    user_keywords = network.getUserKeywords(user)
    keyword_intersect = list(set(user_keywords) & set(query_keywords))
    keyword_union = list(set(user_keywords) | set(query_keywords))
    keyword_score = len(keyword_intersect) / len(keyword_union)
    
    deg_sim = (g * keyword_score) + (h * rel_score)

    result = {
        'user': user,
        'distance': distance,
        'keyword_score': keyword_score,
        'rel_score': rel_score,
        'deg_sim': deg_sim,
        'satisfy': True,
        'children': []
        
    }

    # Once max number of hops has been reached return tree
    if i >= hops:
        return result
    

    # Repeat for each relation of a child
    for r in rels:
        if r[0] not in parents:
            result['children'].append(gen_tree(r[0], query_keywords, query_rels, g, h, network, hops, parents=parents, distance=distance + 1, i=i+1))
    return result


# Remove nodes from the tree that dont satisfy a degree of similarity
# DOES NOT remove nodes which have children that satisfy degSim
def prune_tree(tree, min):
    for c in tree['children']:
        prune_tree(c, min)
        if (c['satisfy'] == False) and (len(c['children']) == 0):
            tree['children'].remove(c)
    if Decimal(tree['deg_sim']) > Decimal(min):
        tree['satisfy'] = False
    return tree

# Traverses tree to generate two list of user
# result_user - satisfy the query
# pass_user - user does not satisfy the quey but are a needed 'hop' between users
def tree_users(tree, result_user=[], pass_user=[]):
    for c in tree['children']:
        tree_users(c, result_user=result_user, pass_user=pass_user)
    
    if tree['satisfy'] == False:
        pass_user.append(tree['user'])
    else:
        result_user.append(tree['user'])

    return result_user, pass_user

if __name__ == '__main__':
    main()
