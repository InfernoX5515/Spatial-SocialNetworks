class Mixin:
    def pruneTree(self, tree):
        for c in list(tree['children']):
            self.pruneTree(tree['children'][c])
            if (tree['children'][c]['satisfy'] == False) and (len(tree['children'][c]['children']) == 0):
                tree['children'].pop(c)
        return tree
    
    def treeUsers(self, tree, result_user=[], pass_user=[]):
        for c in list(tree['children']):
            self.treeUsers(tree['children'][c], result_user=result_user, pass_user=pass_user)
        if (tree['satisfy'] == False):
            pass_user.append(tree['user'])
        if tree['satisfy'] == True:
            result_user.append(tree['user'])  
        return result_user, pass_user


    def communityTree(self, user, query_keywords, query_rels, community_cohesiveness, g, h ,hops, degSim, parents=[], distance=0, i=0):
        # Do not repeat nodes
        parents.append(user)

        rels = self.selectedSocialNetwork.getUserRel(user)
        rel_users = []
        for r in rels:
            rel_users.append(r[0])
        if len(set(query_rels) | set(rel_users)) == 0:
            rel_score = 0
        else:
            rel_score = len(set(query_rels) & set(rel_users)) / len(set(query_rels) | set(rel_users))

        user_keywords = self.selectedSocialNetwork.getUserKeywords(user)
        keyword_intersect = list(set(user_keywords) & set(query_keywords))
        keyword_union = list(set(user_keywords) | set(query_keywords))

        if len(keyword_union) == 0:
            keyword_score = 0
        else:
            keyword_score = len(keyword_intersect) / len(keyword_union)
        
        deg_sim = (g * keyword_score) + (h * rel_score)

        deg_sim_satisfy = deg_sim >= degSim
        if len(keyword_intersect) < community_cohesiveness:
            deg_sim_satisfy = False

        result = {
            'user': user,
            'distance': distance,
            'hops': i,
            'keywords': keyword_union,
            'keyword_score': keyword_score,
            'rel_score': rel_score,
            'deg_sim': deg_sim,
            'satisfy': deg_sim_satisfy,
            'children': {} 
        }

        # Once max number of hops has been reached return tree
        if i >= hops:
            return result
        

        # Repeat for each relation of a child
        for r in rel_users:
            if r not in parents:
                result['children'][r] = self.communityTree(r, query_keywords, query_rels, community_cohesiveness, g, h, hops, degSim, parents=parents, distance=distance + 1, i=i+1)
        return result


    def kdTree(self, queryKeywords, user, keywords, distance, hops, hopDepth=0, currentDist=0,  parents=[]):
        # Do not repeat nodes
        parents.append(user)
        userKeywords = self.selectedSocialNetwork.getUserKeywords(user)
        commonKeywords = list(set(userKeywords) & set(queryKeywords))

        satisfy = False
        if len(commonKeywords) >= keywords and currentDist <= distance:
            satisfy = True

        result = {
            'user': user,
            'distance': currentDist,
            'keywords': commonKeywords,
            'hops': hopDepth,
            'satisfy': satisfy,
            'children': {}
        }

        relations = self.selectedSocialNetwork.getUserRel(user)
        
        # Do not continue after the max number of hops
        if hopDepth >= hops:
            return result

        # Repeat for each relation of a child
        for r in relations:
            if r[0] not in parents:
                result['children'][r[0]] = self.kdTree(queryKeywords, r[0], keywords, distance, hops, hopDepth=hopDepth + 1, currentDist=currentDist + float(r[1]),  parents=parents)
        return result