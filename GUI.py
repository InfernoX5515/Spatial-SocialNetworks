from collections import Counter
from os.path import exists
from os import getenv
from anytree import Node, RenderTree, find_by_attr
from Config import Config
from PyQt5 import QtGui, QtCore
from scipy import spatial
import pyqtgraph as pg
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from RoadNetwork import RoadNetwork
from SocialNetwork import SocialNetwork
from sklearn.cluster import KMeans
from pyvis.network import Network
import networkx as nx
import time
from gui.menubar import MenuBar
from gui.queryInput import QueryInput
from gui.user import UserUI
#from gui.toolbar import Mixin as ToolbarMixin
from gui.toolbar import Toolbar, QueryToolbar, Timeline
from gui.tree import Mixin as TreeMixin
import datetime

class Gui(QtWidgets.QMainWindow, TreeMixin):

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print('Creating the object')
            cls._instance = super(Gui, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        super(Gui, self).__init__()
        # Creates config
        self.config = Config()
        # Plot options
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'white')
        # A dictionary of windows, each window has it's on id
        self.__windows = {}
        # Stores file hierarchy data
        self.__fileTreeObjects = {}
        # Stores timestamps for query time calculation
        self.Qstart = 0
        self.Qend = 0
        self.SummaryResponseTime = 0
        # Stores timestamps for query time calculation
        self.CTstart = 0
        self.CTend = 0
        self.ClusterResponseTime = 0
        # Stores widget instances
        self.roadGraphWidget = None
        self.socialGraphWidget = None
        self.socialNetWidget = QWebEngineView()
        self.summarySelected = False
        self.hidePOIsSelected = False
        # Stores selected network instances
        self.selectedRoadNetwork = None
        self.selectedSocialNetwork = None
        # Query user information
        self.queryUser = None
        self.queryKeyword = None
        self.queryUserPlots = []
        # Store data for interactive network
        self.interactiveNetwork = nx.Graph()
        # Store all network info in dict format {"NetworkName: {"Data": "Value", ...}, ..."}
        self.__roadNetworks = self.config.settings["Road Networks"]
        self.__socialNetworks = self.config.settings["Social Networks"]
        # Store network objects
        self.__roadNetworkObjs = self.createNetworkInstances(self.__roadNetworks, RoadNetwork)
        self.__socialNetworkObjs = self.createNetworkInstances(self.__socialNetworks, SocialNetwork)
        # Set up layout
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(0)
        self.sumLayout = QtWidgets.QGridLayout(self)
        self.sumLayout.setSpacing(0)
        self.view = QtWidgets.QWidget()
        # Initializes menus
        self.__menuBar()
        #self.navToolbar()
        #self.__queryUserButton()
        self.__mainWindow()
        self.__ViewStats()
        # Array for plot points
        self.centers = []
        self.ids = []

        self.toolbar = Toolbar(self)
        self.__windows[3] = QtWidgets.QWidget()
        self.__windows[4] = QtWidgets.QWidget()
        self.__windows[6] = QtWidgets.QWidget()
        self.__windows[7] = QtWidgets.QWidget()
        self.queryInput = QueryInput(self, self.__windows[3], self.__windows[6])
        self.queryUserToolbar = QueryToolbar(self, self.__windows[3], self.__windows[4])
        self.queryUserToolbar.queryUserButton()
        self.toolbar.navToolbar()
        self.timeline = Timeline(self)
        self.timeline.show()
        self.timeline.setDates(120, 240)

    # Creates the plot widgets. suffix is used when a summary graph is created, for example
    def createPlots(self, suffix=""):
        self.roadGraphWidget = self.win.addPlot(row=0, col=1, title=f"Road Network {suffix}")
        self.roadGraphWidget.scene().sigMouseClicked.connect(self.roadGraphClick)
        self.socialGraphWidget = self.win.addPlot(row=0, col=0, title=f"Social Network {suffix}")
        #self.linkGraphAxis()

    def roadGraphClick(self, event):
        vb = self.roadGraphWidget.vb
        cords = event.scenePos()
        if self.roadGraphWidget.sceneBoundingRect().contains(cords):
            point = vb.mapSceneToView(cords)
            tree = spatial.KDTree(self.centers)
            closest_point = tree.query([[point.x(), point.y()]])[1][0]
            ui = UserUI(self, self.__windows[7])
            ui.showClusterUsers(self.selectedSocialNetwork.getClusterUsers(self.ids[closest_point]))

    def createSumPlot(self, suffix=None):
        self.roadGraphWidget = self.win.addPlot(row=0, col=1, title=f"Road Network {suffix}")

    # Displays main window
    def __mainWindow(self):
        # Set up window
        screensize = self.screen().availableSize().width(), self.screen().availableSize().height()
        self.setGeometry(int((screensize[0] / 2) - 500), int((screensize[1] / 2) - 300), 1000, 600)
        self.setWindowTitle("Spatial-Social Networks") 
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.win = pg.GraphicsLayoutWidget()
        self.sum = pg.GraphicsLayoutWidget()
        with open('nx.html', 'r') as f:
            html = f.read()
            self.socialNetWidget.setHtml(html)
        # Define default layout
        self.layout.addWidget(self.win, 0, 0, 1, 2)
        # self.toolbar.navToolbar()
        self.view.setLayout(self.layout)
        self.setCentralWidget(self.view)
        # Create and set up graph widget
        self.createPlots()
        # Show window
        self.show()
    
        
    def __keywordCommunity(self):
        self.queryInput.community()

    def __keywordTimeCommunity(self):
        self.queryInput.communityTime()

    def __queryInput(self):
        self.queryInput.kdQuery()

    def __menuBar(self):
        menu = MenuBar(self.menuBar())

        menu.addMenu("File")
        menu.addChild("Files", "File", shortcut="Ctrl+f", tooltip="View files", action=self.viewFiles)

        menu.addMenu("View")
        menu.createGroup("ViewGroup", self)
        menu.addChild("Summary View", "View", group="ViewGroup", tooltip="View summary graphs", action=self.viewSummary)
        menu.addChild("Full View", "View", group="ViewGroup", tooltip="View full graphs", action=self.viewSummary,
                      checked=True)

        networks = self.getCompleteNetworks()
        sNetworks = networks["Social Networks"]
        rNetworks = networks["Road Networks"]

        menu.addMenu("Social Networks")
        menu.createGroup("SocialNetworkGroup", self)
        menu.addChild("None", "Social Networks", group="SocialNetworkGroup", tooltip="Display no social network",
                      action=lambda j: self.displaySocialNetwork(None), checked=True)
        for x in sNetworks:
            menu.addChild(x, "Social Networks", group="SocialNetworkGroup",
                          tooltip=f"Switch to view social network {x}",
                          action=lambda j, a=x: self.displaySocialNetwork(a))

        menu.addMenu("Road Networks")
        menu.createGroup("RoadNetworkGroup", self)
        menu.addChild("None", "Road Networks", group="RoadNetworkGroup", tooltip="Display no road network",
                      action=lambda j: self.displayRoadNetwork(None), checked=True)
        for x in rNetworks:
            menu.addChild(x, "Road Networks", group="RoadNetworkGroup",
                          tooltip=f"Switch to view road network {x}",
                          action=lambda j, a=x: self.displayRoadNetwork(a))
            
        # Add menu for stats
        menu.addMenu("Statistics")
        menu.addChild("View", "Statistics", tooltip="View statistics", action=self.ShowStatsWindow)


        menu.addMenu("Query")
        menu.addChild("kd-truss", "Query", tooltip="kd-truss menu", action=self.__queryInput)
        menu.addChild("Community Search", "Query", tooltip="community search menu", action=self.__keywordCommunity)
        menu.addChild("Community Search w/ Time", "Query", tooltip="community search w/ time menu", action=self.__keywordTimeCommunity)

    def clearView(self):
        self.win.removeItem(self.roadGraphWidget)
        if self.socialGraphWidget:
            self.win.removeItem(self.socialGraphWidget)
        if self.queryUserPlots:
            self.queryUserPlots = []
        self.roadGraphWidget = None
        self.socialGraphWidget = None

    def dijkstra(self, queryUser):
        '''if self.selectedRoadNetwork is not None:
            visited = []
            numOfV = self.selectedRoadNetwork.nodeCount()
            D = {v: float('inf') for v in range(numOfV)}
            startVertex = self.selectedRoadNetwork.closestNode(queryUser[1][0][0], queryUser[1][0][1])
            D[startVertex] = 0
            pq = PriorityQueue()
            pq.put((0, startVertex))
            while not pq.empty():
                (dist, current_vertex) = pq.get()
                visited.append(current_vertex)
                for neighbor in range(current_vertex - 200, current_vertex + 200):
                    edge = self.selectedRoadNetwork.isAnEdge(str(float(current_vertex)), str(float(neighbor)))
                    if edge is not None:
                        distance = self.selectedRoadNetwork.getEdgeDistance(str(edge))
                        if neighbor not in visited:
                            old_cost = D[neighbor]
                            new_cost = D[current_vertex] + float(distance)
                            if new_cost < old_cost:
                                pq.put((new_cost, neighbor))
                                D[neighbor] = new_cost
            print(D)'''

    # Handles summary view
    def viewSummary(self):
        # Switch view to summary
        if not self.summarySelected:
            self.summarySelected = True
            self.clearView()
            # Displays summary plots
            self.createSumPlot("Summary")
            self.socialNetWidget = QWebEngineView()
            with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)
            # Setup summary view
            self.view = QtWidgets.QWidget()
            self.sumLayout = QtWidgets.QGridLayout()
            
            self.sumLayout.setSpacing(0)
            self.sumLayout.addWidget(self.socialNetWidget, 0, 0, 2,1)
            self.sumLayout.addWidget(self.win, 0, 1)
            self.sumLayout.setColumnStretch(0, 1)
            self.sumLayout.setColumnStretch(1, 1)
            self.toolbar.navToolbar()
            self.view.setLayout(self.sumLayout)
            self.setCentralWidget(self.view)
            self.toolbar.clusterInput()
            #self.__queryInput()
            self.updateSummaryGraph()

        # Switch view to main
        else:
            self.summarySelected = False
            # Setup default view
            self.view = QtWidgets.QWidget()
            self.layout = QtWidgets.QGridLayout()
            self.layout.setSpacing(0)
            self.layout.addWidget(self.win, 0, 0, 1, 2)
            # Add graph toolbars
            self.toolbar.navToolbar()
            self.view.setLayout(self.layout)
            self.setCentralWidget(self.view)
            self.toolbar.clusterInput.close()
            self.clearView()
            #self.queryInput.close()
            self.createPlots()
            # Re-visualize selected networks
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.plotQueryUser()

    def visualizeSummaryData(self, ids, centers, sizes, relations, popSize):
     
        # Note: For some reason, the alpha value is from 0-255 not 0-100
        self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                  symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))

        # Create Interactive Graph HTML File Using pyvis
        queryCluster = -1
        if self.queryUser is not None:
            queryCluster = self.selectedSocialNetwork.getUserCluster(self.queryUser[0])
        network = nx.Graph()
        for i in range(0, len(centers)):
            if ids[i] == queryCluster:
                network.add_node(str(centers[i][0]) + str(centers[i][1]), physics=False, label=popSize[i], color='green',shape='star')
            else:
                network.add_node(str(centers[i][0]) + str(centers[i][1]), physics=False, label=popSize[i])
        for i in range(1, len(relations[0])):
            network.add_edge(str(relations[0][i]) + str(relations[1][i]),
                             str(relations[0][i - 1]) + str(relations[1][i - 1]))
        nt = Network()
        nt.from_nx(network)
        nt.save_graph('nx.html')
        # LEGACY SOCIAL NETWORK GRAPH
        #self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
        #                            symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 150))
        #self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 100),
        #                            brush=(50, 50, 200, 100))

    def updateSummaryGraph(self):
        self.Qstart = time.time()
        # Clears last view
        if self.summarySelected:
            self.clearView()
        self.createSumPlot("Summary")
        self.socialNetWidget.reload()
        # If a road network is selected, display info
        if self.selectedRoadNetwork is not None:
            self.selectedRoadNetwork.visualize(self.roadGraphWidget)   
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.toolbar.clusterInput.textBox.text())
            self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
            with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)
        self.plotQueryUser()
        self.Qend = time.time()
        self.__UpdateQueryTime()


    def interactiveKdVisualNodes(self, tree, graph=nx.Graph()):
        tempTitle = '<p>Number of hops: ' + str(tree["hops"]) + '</p><p>Distance: ' + str(tree["distance"]) + '</p><p>Common Keywords:</p><ol>'
        for key in tree["keywords"]:
            tempTitle += '<li>' + str(self.selectedSocialNetwork.getKeywordByID(key)) + '</li>'
        tempTitle += '</ol>'
        if tree["satisfy"] == True:
            graph.add_node(tree["user"], physics=False, label=str(tree["user"]), color='blue', size=15, title=tempTitle)
        else:
            graph.add_node(tree["user"], physics=False, label=str(tree["user"]), color='grey', size=15, title=tempTitle)
        for c in list(tree["children"]):
            self.interactiveKdVisualNodes(tree["children"][c], graph)
        return graph
    
    def interactiveCommunityVisualNodes(self, tree, graph=nx.Graph()):
        tempTitle = '<p>Number of hops: ' + str(tree["hops"]) + '</p><p>Distance: ' + str(tree["distance"]) + '</p><p>Degree of Similarity:</p>' + str(tree["deg_sim"]) + '<p>Common Keywords:</p><ol>'
        for key in tree["keywords"]:
            tempTitle += '<li>' + str(self.selectedSocialNetwork.getKeywordByID(key)) + '</li>'
        tempTitle += '</ol>'
        if tree["satisfy"] == True:
            graph.add_node(tree["user"], physics=False, label=str(tree["user"]), color='blue', size=15, title=tempTitle)
        else:
            graph.add_node(tree["user"], physics=False, label=str(tree["user"]), color='grey', size=15, title=tempTitle)
        for c in list(tree["children"]):
            self.interactiveCommunityVisualNodes(tree["children"][c], graph)
        return graph

    #def visualizeKdData(self, users, keys, hops, dists):
    def visualizeKdData(self, kdTree):
        if self.queryUser is not None:
            """ 

            Interactive code has been moved to the KDTrust class

            # Create Interactive Graph HTML File Using pyvis
            network = nx.Graph()
            titleTemp = '<p>Keywords:</p><ol>'
            # Add query user
            queryKeys = self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            for key in queryKeys:
                titleTemp += '<li>' + str(self.selectedSocialNetwork.getKeywordByID(key)) + '</li>'
            titleTemp += '</ol>'
            network.add_node(self.queryUser[0], physics=False, label=str('Query: ') + str(int(float(self.queryUser[0]))),
                             color='green', size=15, shape='star', title=titleTemp)
            # Add common users
            common = self.selectedSocialNetwork.userLoc(self.queryUser[0])
            commonLoc = self.selectedRoadNetwork.findNearest(common)
            for user in users:
                query = self.selectedSocialNetwork.userLoc(user)
                d = dists[user]
                h = hops[user]
                if h == -1:
                    h = 1
                k = keys[user]
                temp = '<p>Number of hops: ' + str(h) + '</p><p>Distance: ' + str(d) + '</p><p>Common Keywords:</p><ol>'
                for key in k:
                    temp += '<li>' + str(self.selectedSocialNetwork.getKeywordByID(key)) + '</li>'
                temp += '</ol>'
                if user != self.queryUser[0]:
                    network.add_node(user, physics=False, label=str(int(float(user))), color='blue', title=temp)
                rels = self.selectedSocialNetwork.commonRelations(user, users)
                for rel in rels:
                    network.add_edge(rel, user, color='blue')
            """




            graph = self.interactiveKdVisualNodes(kdTree, graph=nx.Graph())
            titleTemp = '<p>Keywords:</p><ol>'
            # Add query user
            queryKeys = self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            for key in queryKeys:
                titleTemp += '<li>' + str(self.selectedSocialNetwork.getKeywordByID(key)) + '</li>'
            titleTemp += '</ol>'
            graph.add_node(self.queryUser[0], physics=False, label=str('Query: ') + str(int(float(self.queryUser[0]))),
                                color='green', size=15, shape='star', title=titleTemp)


            result_users, pass_users = self.treeUsers(kdTree, [], [])
            all_users = set(result_users) | set(pass_users)
            for u in all_users:
                rels = self.selectedSocialNetwork.getUserRel(u)
                rel_users = []
                for r in rels:
                    rel_users.append(r[0])
                relations = set(rel_users) & set(all_users)
                for r in relations:
                    graph.add_edge(u, r, color='black')
            nt = Network()
            nt.from_nx(graph)
            nt.save_graph('kd-trust.html')

            qu = self.queryUser[0]
            self.clearView()
            self.createSumPlot()
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.toolbar.clusterInput.textBox.text())
            self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
            self.setQueryUser(qu)
            

            for user in result_users:
                temp = self.selectedSocialNetwork.userLoc(user)
                self.roadGraphWidget.plot([float(temp[0][0])], [float(temp[0][1])], pen=None, symbol='o', symbolSize=20,
                                          symbolPen=(50, 50, 200, 25), symbolBrush=(50, 50, 200, 175))
                #network.add_edge(self.queryUser[0], user, color='red')
            self.plotQueryUser()
            #nt = Network('100%', '100%')
            #nt.from_nx(network)
            #nt.save_graph('nx.html')

    
    def updateKdSummaryGraph(self):
        self.socialNetWidget.reload()
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            #kd, keys, hops, dists = self.getKDTrust(self.__windows[6].kTextBox.text(), self.__windows[6].dTextBox.text(),
            #                     self.__windows[6].eTextBox.text())
            #self.visualizeKdData(kd, keys, hops, dists)
            self.CTstart = time.time()
            res = self.queryInput.getKdResponse()
            kdTree = self.getKDTrust(res[0], res[1], res[2])
            self.visualizeKdData(kdTree)
            # Stop counting time for query
            self.CTend = time.time()
            self.__UpdateQueryTime()
            with open('kd-trust.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)


    def visualizeCommunityData(self, kdTree):
        if self.queryUser is not None:

            graph = self.interactiveCommunityVisualNodes(kdTree, graph=nx.Graph())
            titleTemp = '<p>Keywords:</p><ol>'
            # Add query user
            queryKeys = self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            for key in queryKeys:
                titleTemp += '<li>' + str(self.selectedSocialNetwork.getKeywordByID(key)) + '</li>'
            titleTemp += '</ol>'
            graph.add_node(self.queryUser[0], physics=False, label=str('Query: ') + str(int(float(self.queryUser[0]))),
                                color='green', size=15, shape='star', title=titleTemp)


            result_users, pass_users = self.treeUsers(kdTree, [], [])
            all_users = set(result_users) | set(pass_users)
            for u in all_users:
                rels = self.selectedSocialNetwork.getUserRel(u)
                rel_users = []
                for r in rels:
                    rel_users.append(r[0])
                relations = set(rel_users) & set(all_users)
                for r in relations:
                    graph.add_edge(u, r, color='black')
            nt = Network()
            nt.from_nx(graph)
            nt.save_graph('community-query.html')

            qu = self.queryUser[0]
            #self.clearView()
            
            self.win.removeItem(self.roadGraphWidget)
            self.roadGraphWidget = None
            self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Community Query")
            self.roadGraphWidget.clear()

            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            #self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.clusterInput.textBox.text())
            #self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)

            
            x = []
            y = []
            for user in result_users:
                user_location = self.selectedSocialNetwork.userLoc(user)
                x.append(float(user_location[0][0]))
                y.append(float(user_location[0][1]))
            self.roadGraphWidget.plot(x, y, pen=None, symbol='o', symbolSize=10,
                                          symbolPen=(50, 50, 200, 100), symbolBrush=(50, 50, 200, 175))
            #self.setQueryUser(qu)
                #network.add_edge(self.queryUser[0], user, color='red')
            #self.plotQueryUser()
            if self.queryUser is not None:
                if not self.queryUserPlots:
                    [a.clear() for a in self.queryUserPlots]
                self.queryUserPlots = []
                color = 'green'
                for loc in self.queryUser[1]:
                    self.queryUserPlots.append(self.roadGraphWidget.plot([float(loc[0])], [float(loc[1])], pen=None,
                                                                        symbol='star', symbolSize=30, symbolPen=color,
                                                                        symbolBrush=color))


    def updateCommunitySummaryGraph(self):
        self.socialNetWidget.reload()
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            queryKeywords = self.queryInput.getCommunityKeywords()
            queryKeywords += self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            queryRelsRaw = self.selectedSocialNetwork.getUserRel(self.queryUser[0])
            queryRels = []
            for r in queryRelsRaw:
                queryRels.append(r[0])
            self.CTstart = time.time()
            #community = self.communityTree(self.queryUser[0], queryKeywords, queryRels, float(self.__windows[6].kcTextBox.text()), float(self.__windows[6].kTextBox.text()), float(self.__windows[6].rTextBox.text()), float(self.__windows[6].dTextBox.text()), float(self.__windows[6].eTextBox.text()),[], 0, 0)
            res = self.queryInput.getCommunityResponse()
            community = self.communityTree(self.queryUser[0], queryKeywords, queryRels, float(res[0]), float(res[3]), float(res[4]), float(res[1]), float(res[2]), [], 0, 0)
            community = self.pruneTree(community)
            self.visualizeCommunityData(community)
            # Stop counting time for query
            self.CTend = time.time()
            self.__UpdateQueryTime()
            with open('community-query.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)

    def updateTimeline(self):
        values = self.timeline.getDates()
        # convert from int to dates
        start = str(datetime.date(2020, 1, 1) + datetime.timedelta(days=values[0]))
        end = str(datetime.date(2020, 1, 1) + datetime.timedelta(days=values[1]))

        self.socialNetWidget.reload()
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            queryKeywords = self.queryInput.getCommunityKeywords()
            queryKeywords += self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            queryRelsRaw = self.selectedSocialNetwork.getUserRel(self.queryUser[0])
            res = self.queryInput.getCommunityTimeResponse()
            queryPois = self.selectedSocialNetwork.getUserPoiInTime(self.queryUser[0], start, end)
            queryRels = []
            for r in queryRelsRaw:
                queryRels.append(r[0])
            self.CTstart = time.time()
            #community = self.communityTree(self.queryUser[0], queryKeywords, queryRels, float(self.__windows[6].kcTextBox.text()), float(self.__windows[6].kTextBox.text()), float(self.__windows[6].rTextBox.text()), float(self.__windows[6].dTextBox.text()), float(self.__windows[6].eTextBox.text()),[], 0, 0)
            
#def communityTimeTree(self, user, query_keywords, query_rels, query_pois, start, end, community_cohesiveness, g, h, j, hops, degSim, parents=[], distance=0, i=0):
            community = self.communityTimeTree(
                self.queryUser[0], 
                queryKeywords, 
                queryRels, 
                queryPois, 
                start,
                end,
                float(res[0]), 
                float(res[3]), 
                float(res[4]),
                float(res[5]), 
                float(res[1]), 
                float(res[2]), 
                [], 
                0,
                0)
            community = self.pruneTree(community)
            self.visualizeCommunityData(community)
            # Stop counting time for query
            self.CTend = time.time()
            self.__UpdateQueryTime()
            with open('community-query.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)

        
    
    def updateCommunityTimeSummaryGraph(self):
        self.socialNetWidget.reload()
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            queryKeywords = self.queryInput.getCommunityKeywords()
            queryKeywords += self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            queryRelsRaw = self.selectedSocialNetwork.getUserRel(self.queryUser[0])
            res = self.queryInput.getCommunityTimeResponse()
            queryPois = self.selectedSocialNetwork.getUserPoiInTime(self.queryUser[0], res[6], res[7])
            queryRels = []
            for r in queryRelsRaw:
                queryRels.append(r[0])
            self.CTstart = time.time()
            #community = self.communityTree(self.queryUser[0], queryKeywords, queryRels, float(self.__windows[6].kcTextBox.text()), float(self.__windows[6].kTextBox.text()), float(self.__windows[6].rTextBox.text()), float(self.__windows[6].dTextBox.text()), float(self.__windows[6].eTextBox.text()),[], 0, 0)
            
#def communityTimeTree(self, user, query_keywords, query_rels, query_pois, start, end, community_cohesiveness, g, h, j, hops, degSim, parents=[], distance=0, i=0):
            community = self.communityTimeTree(
                self.queryUser[0], 
                queryKeywords, 
                queryRels, 
                queryPois, 
                res[6],
                res[7],
                float(res[0]), 
                float(res[3]), 
                float(res[4]),
                float(res[5]), 
                float(res[1]), 
                float(res[2]), 
                [], 
                0,
                0)
            community = self.pruneTree(community)
            self.visualizeCommunityData(community)
            # Stop counting time for query
            self.CTend = time.time()
            self.__UpdateQueryTime()
            with open('community-query.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)

    #Generate kdtrust from input
    def getKDTrust(self, keywords, hops, distance):
        if self.queryUser is not None:
 
            #kd = KDTrust(self.selectedRoadNetwork, self.selectedSocialNetwork, self.queryUser[0], float(keywords), float(distance), float(hops))
            queryKeywords = self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])


            if float(distance) == 0.0:
                distance = 9999.0

            print(distance)

            kdTree = self.kdTree(queryKeywords, self.queryUser[0], float(keywords), float(distance), float(hops), 0, 0, [])
            kdTree = self.pruneTree(kdTree)
            """
            # Users with common keywords
            common, keys = self.usersCommonKeyword(k=float(keywords))
            # Narrow query down to users within hops
            common, hops = self.usersWithinHops(common, h=float(hops))
            # Narrow down with degree of similarity distance (longest compute time)
            common, dists = self.usersWithinDistance(common, d=float(distance))

            neighbors = []
            for user in common:
                path = self.selectedSocialNetwork.shortestPath(self.queryUser[0], user)
                print(path)
                neighbors = list(set(neighbors) | set(path))
            print(neighbors)
            
            common = []
            keys = []
            hops = []
            dists = []
            users = kd.getUsers()
            """
            return kdTree
        

    def __UpdateQueryTime(self):
        self.SummaryResponseTime = (self.Qend - self.Qstart) * 1000
        self.ClusterResponseTime = (self.CTend - self.CTstart) * 1000
        self.__ViewStats()

    # Returns query user in form [id, [[lat, lon], [lat, lon]]]
    def setQueryUser(self, user, window=4):
        if self.queryUser is not None:
            [a.clear() for a in self.queryUserPlots]
            self.queryUserPlots = []
        self.queryUser = self.selectedSocialNetwork.getUser(user)
        self.plotQueryUser()
        self.queryUserToolbar.userLabel.setText(user.split(".0")[0])
        #self.usersCommonKeyword()
        self.__windows[window].close()
        self.dijkstra(self.queryUser)

    def plotQueryUser(self):
        if self.queryUser is not None:
            if not self.queryUserPlots:
                [a.clear() for a in self.queryUserPlots]
            self.queryUserPlots = []
            color = 'green'
            for loc in self.queryUser[1]:
                if self.summarySelected:
                    self.clearView()
                    self.plottingUserRefresh()
                self.queryUserPlots.append(self.roadGraphWidget.plot([float(loc[0])], [float(loc[1])], pen=None,
                                                                     symbol='star', symbolSize=30, symbolPen=color,
                                                                     symbolBrush=color))

    def plottingUserRefresh(self):
        self.createSumPlot("Summary")
        self.socialNetWidget.reload()
        if self.selectedRoadNetwork is not None:
            self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
           self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(
                self.toolbar.clusterInput.textBox.text())
           self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
           with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)


    def setQueryKeyword(self, keyword):
        self.queryKeyword = keyword
        self.queryUserToolbar.keywordLabel.setText(self.selectedSocialNetwork.getKeywordByID(keyword))
        self.__windows[5].close()

    # Display for loading networks
    def viewFiles(self):
        # Set up hierarchy base
        self.__fileTreeObjects = {
            '0': QtWidgets.QTreeWidgetItem(["Road Networks"]),
            '1': QtWidgets.QTreeWidgetItem(["Social Networks"])
        }
        # Set up tree widget
        self.__windows[0] = pg.TreeWidget()
        self.__windows[0].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[0].setDragEnabled(False)
        self.__windows[0].header().setSectionsMovable(False)
        self.__windows[0].header().setStretchLastSection(False)
        self.__windows[0].header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.__windows[0].setWindowTitle('Network Files')
        self.__windows[0].setColumnCount(2)
        self.__windows[0].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        # Show TreeWidget
        self.__windows[0].show()
        # Add Road Networks and Social Networks to hierarchy
        self.__windows[0].addTopLevelItem(self.__fileTreeObjects['0'])
        self.__windows[0].addTopLevelItem(self.__fileTreeObjects['1'])
        # Add button to add a new Road Network
        nrn = QtWidgets.QPushButton("New Road Network")
        nrn.clicked.connect(lambda: self.newNetwork("road"))
        self.__windows[0].setItemWidget(self.__fileTreeObjects['0'], 1, nrn)
        # Add button to add a new Social Network
        nsn = QtWidgets.QPushButton("New Social Network")
        nsn.clicked.connect(lambda: self.newNetwork("social"))
        self.__windows[0].setItemWidget(self.__fileTreeObjects['1'], 1, nsn)
        # Adds all sub-objects to roadNetworks. Each element is given a number in order for the hierarchy. For example,
        # 1.3 is the fourth child of the second element
        i = 0
        for x in self.__roadNetworks:
            i += 1
            self.__fileTreeObjects[f"0.{i}"] = QtWidgets.QTreeWidgetItem([x])
            self.__fileTreeObjects['0'].addChild(self.__fileTreeObjects[f"0.{i}"])
            j = 0
            # Adds files
            cFile = {}
            for y in self.__roadNetworks[x]:
                j += 1
                iName = self.__roadNetworks[x][y]
                if iName != f"[{iName}]":
                    iNameArr = iName.split("/")
                    iName = iNameArr[len(iNameArr) - 1]
                self.__fileTreeObjects[f"0.{i}.{j}"] = QtWidgets.QTreeWidgetItem([iName])
                self.__fileTreeObjects[f"0.{i}"].addChild(self.__fileTreeObjects[f"0.{i}.{j}"])
                cFile[j] = QtWidgets.QPushButton("Choose File")
                cFile[j].clicked.connect(
                    lambda junk, a=i, d=j, b=x, c=y: self.chooseFile(f"0.{a}.{d}", "Road Network", b, c))
                self.__windows[0].setItemWidget(self.__fileTreeObjects[f"0.{i}.{j}"], 1, cFile[j])
        # Adds all sub-objects to socialNetworks. Each element is given a number in order for the hierarchy. For
        # example, 1.3 is the fourth child of the second element
        i = 0
        cFileS = {}
        for x in self.__socialNetworks:
            i += 1
            self.__fileTreeObjects[f"1.{i}"] = QtWidgets.QTreeWidgetItem([x])
            self.__fileTreeObjects['1'].addChild(self.__fileTreeObjects[f"1.{i}"])
            j = 0
            # Adds files
            for y in self.__socialNetworks[x]:
                j += 1
                iName = self.__socialNetworks[x][y]
                if iName != f"[{iName}]":
                    iNameArr = iName.split("/")
                    iName = iNameArr[len(iNameArr) - 1]
                self.__fileTreeObjects[f"1.{i}.{j}"] = QtWidgets.QTreeWidgetItem([iName])
                self.__fileTreeObjects[f"1.{i}"].addChild(self.__fileTreeObjects[f"1.{i}.{j}"])
                cFileS[f"{j}.{j}"] = QtWidgets.QPushButton("Choose File")
                cFileS[f"{j}.{j}"].clicked.connect(
                    lambda junk, a=i, b=j, c=x, d=y: self.chooseFile(f"1.{a}.{b}", "Social Network", c, d))
                self.__windows[0].setItemWidget(self.__fileTreeObjects[f"1.{i}.{j}"], 1, cFileS[f"{j}.{j}"])

    # TODO: Fix issue where networks aren't loaded after they are created -- program requires restart
    # Creates a new Road network
    def newNetwork(self, type):
        if type != "road" and type != "social":
            print("ERROR: newNetwork() must have type road or social")
            exit(0)
        title = ""
        network = None
        num = -1
        if type == "road":
            title = "Road Network"
            network = self.__roadNetworks
            num = 0
        elif type == "social":
            title = "Social Network"
            num = 1
            network = self.__socialNetworks
        self.__windows[1] = QtWidgets.QInputDialog()
        text, ok = self.__windows[1].getText(self, f'New {title}', f"Enter your {title.lower()} name:")
        text = str(text)
        # If the road network does not exist already, add it to the config
        if ok and text not in network.keys() and text != "":
            if type == "road":
                network[text] = {
                    "nodeFile": "[nodeFile]",
                    "edgeFile": "[edgeFile]",
                    "POIFile": "[POIFile]",
                    "keyFile": "[keyFile]",
                    "keyMapFile": "[keyMapFile]"
                }
            elif type == "social":
                network[text] = {
                    "locFile": "[locFile]",
                    "relFile": "[relFile]",
                    "keyFile": "[keyFile]",
                    "keyMapFile": "[keyMapFile]",
                    "userDataFile": "[userDataFile]",
                    "userPoiFile": "[userPoiFile]"
                }
            # Adds new road network to tree
            keys = list(network.keys())
            currItem = len(keys) + 1
            # Add new road network to hierarchy
            self.__fileTreeObjects[f"{num}.{currItem}"] = QtWidgets.QTreeWidgetItem([text])
            self.__fileTreeObjects[f'{num}'].addChild(self.__fileTreeObjects[f"{num}.{currItem}"])
            for i in range(1, len(network[text]) + 1):
                self.__fileTreeObjects[f"{num}.{currItem}.{i}"] = \
                    QtWidgets.QTreeWidgetItem([network[text]
                                               [f"{list(network[text].keys())[i - 1]}"]])
                self.__fileTreeObjects[f'{num}.{currItem}'].addChild(self.__fileTreeObjects[f"{num}.{currItem}.{i}"])
                addN = QtWidgets.QPushButton("Choose File")
                addN.clicked.connect(lambda junk, a=num, b=i, c=currItem, d=title, e=text: self.chooseFile(
                    f"{a}.{c}.{b}", f"{d}", e, f"{list(network[e].keys())[b - 1]}"))
                self.__windows[0].setItemWidget(self.__fileTreeObjects[f"{num}.{currItem}.{i}"], 1, addN)
            # Update config
            self.config.update(f"{title}s", network)

    # TODO: Implement for summary graph
    def hidePOIs(self, checked):
        if checked:
            self.clearView()
            self.createPlots()
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            #self.linkGraphAxis()
        else:
            self.clearView()
            self.createPlots()
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            self.selectedRoadNetwork.visualize(None, self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            #self.linkGraphAxis()

    def chooseFile(self, obj, T, network, sub):
        self.__windows[2] = QtWidgets.QFileDialog()
        pathArr = self.__windows[2].getOpenFileNames(None, f'Select {sub}', getenv('HOME'), "csv(*.csv)")[0]
        if len(pathArr) != 0:
            path = pathArr[0]
            if T == "Road Network":
                self.__roadNetworks[network][sub] = path
                self.config.update("Road Networks", self.__roadNetworks)
            elif T == "Social Network":
                self.__socialNetworks[network][sub] = path
                self.config.update("Social Networks", self.__socialNetworks)
            # Update item
            fileNameArr = path.split("/")
            fileName = fileNameArr[len(fileNameArr) - 1]
            self.__fileTreeObjects[obj].setText(0, fileName)
        self.menuBar().clear()
        self.__menuBar()

    # Return road networks that have all files and those files exist
    def getCompleteNetworks(self):
        networks = {"Social Networks": [],
                    "Road Networks": []}
        keys = self.__roadNetworks.keys()
        # Road networks
        for i in keys:
            passed = True
            for j in self.__roadNetworks[i]:
                if passed and (self.__roadNetworks[i][j] == f"[{j}]" or not exists(self.__roadNetworks[i][j])):
                    passed = False
            if passed:
                networks["Road Networks"].append(i)
        # Social networks
        keys = self.__socialNetworks.keys()
        for k in keys:
            passed = True
            for l in self.__socialNetworks[k]:
                if passed and (self.__socialNetworks[k][l] == f"[{l}]" or not exists(self.__socialNetworks[k][l])):
                    passed = False
            if passed:
                networks["Social Networks"].append(k)
        return networks

    def displayRoadNetwork(self, network):
        # If the summary is not selected
        if not self.summarySelected:
            self.clearView()
            self.selectedRoadNetwork = None
            self.createPlots()
            # Display road network
            if network is not None:
                # Visualizes the graph that is being selected
                self.__roadNetworkObjs[network].visualize(self.roadGraphWidget)
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
            # Display social network
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.plotQueryUser()
            #self.linkGraphAxis()
        # If the summary is selected
        else:
            self.clearView()
            self.selectedRoadNetwork = None
            self.createSumPlot("Summary")
            # Display road network
            if network is not None:
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            # Draw social network
            if self.selectedSocialNetwork is not None:
                self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.toolbar.clusterInput.textBox.text())
                self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
            self.plotQueryUser()
            #self.linkGraphAxis()

    def displaySocialNetwork(self, network):
        self.queryUser = None
        [a.clear() for a in self.queryUserPlots]
        self.queryUserPlots = []
        #self.queryUserToolbar.userLabel.setText("None")
        self.queryKeyword = None
        #self.queryUserToolbar.keywordLabel.setText("None")
        # If main view
        if not self.summarySelected:
            self.clearView()
            self.selectedSocialNetwork = None
            self.createPlots()
            # Re-visualizes the road network if it is selected
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            # Visualizes social network
            if network is not None:
                self.__socialNetworkObjs[network].visualize(self.socialGraphWidget, self.roadGraphWidget)
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
            #self.linkGraphAxis()
        # If summary view
        else:
            # Removes both graphs to clear them then re-adds them
            self.clearView()
            self.createSumPlot()
            self.selectedSocialNetwork = None
            #self.createPlots("Summary")
            # Re-visualizes the road network if it is selected
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            # Draw cross-hairs on graph
            if network is not None:
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
                self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.toolbar.clusterInput.textBox.text())
                self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)

    # Creates network instances based on text data dictionary of {"NetworkName": {"Data":"Value", ...}
    # If the value is not set, square brackets denote that it is not set, written as "[Value]"
    @staticmethod
    def createNetworkInstances(data, type):
        instances = {}
        # Loops through all networks
        for network in data:
            kwargs = {}
            # Loops through all data in each network
            for dataKey in data[network]:
                dataValue = data[network][dataKey]
                # If the value is set, use it to create the instance
                if dataValue != f"[{dataKey}]":
                    kwargs[dataKey] = dataValue
            instances[network] = type(network, **kwargs)
        return instances

    # Links X and Y axis on main social network and road network graphs
    def linkGraphAxis(self):
        self.socialGraphWidget.setXLink(self.roadGraphWidget)
        self.socialGraphWidget.setYLink(self.roadGraphWidget)


    def __ViewStats(self):
        self.__windows[8] = QtWidgets.QWidget()
        self.__windows[8].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[8].setWindowTitle('Statistics')
        self.__windows[8].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        
        StatsLayout = QtWidgets.QVBoxLayout(self)
        SummaryTimeLabel = QtWidgets.QLabel("Summary Response Time: " + str("{0:.3f}".format(self.SummaryResponseTime)) + " ms")
        StatsLayout.addWidget(SummaryTimeLabel)
        ClusterTimeLabel = QtWidgets.QLabel("Query Response Time: " + str("{0:.3f}".format(self.ClusterResponseTime)) + " ms")
        StatsLayout.addWidget(ClusterTimeLabel)
        StatsLayout.addStretch()
        
        self.__windows[8].setLayout(StatsLayout)
    

    
    def ShowStatsWindow(self):
        self.__windows[8].show()



    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Closed")
        exit(0)
