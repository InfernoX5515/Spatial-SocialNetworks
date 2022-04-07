from collections import Counter
from os.path import exists
from os import getenv
from queue import PriorityQueue

from matplotlib import interactive
from matplotlib.pyplot import title
from Config import Config
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWebEngineWidgets import QWebEngineView
from RoadNetwork import RoadNetwork
from SocialNetwork import SocialNetwork
from sklearn.cluster import KMeans
from pyvis.network import Network
import networkx as nx
# import pyvis
import time
# import matplotlib.pyplot as plt # importing matplotlib package and pyplot is for displaying the graph on canvas


# =====================================================================================================================
#
#   Authors: Halie Eckert, Gavin Hulvey, Sydney Zuelzke
#   Date: 11/3/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       GUI.py is the main class for the GUI. This class handles all guis, sub guis, variables, and object needed
#    to display data.
#
# =====================================================================================================================


class Gui(QtWidgets.QMainWindow):
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
        self.layout = QtWidgets.QHBoxLayout(self)
        self.sumLayout = QtWidgets.QHBoxLayout(self)
        self.view = QtWidgets.QWidget()
        # Initializes menus
        self.__menuBar()
        self.__navToolbar()
        self.__queryUserButton()
        self.__mainWindow()

    # Creates the plot widgets. suffix is used when a summary graph is created, for example
    def createPlots(self, suffix=""):
        self.roadGraphWidget = self.win.addPlot(row=0, col=1, title=f"Road Network {suffix}")
        self.socialGraphWidget = self.win.addPlot(row=0, col=0, title=f"Social Network {suffix}")
        self.linkGraphAxis()

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
        self.layout.addWidget(self.win)
        self.view.setLayout(self.layout)
        self.setCentralWidget(self.view)
        # Create and set up graph widget
        self.createPlots()
        # Show window
        self.show()

    @staticmethod
    def getZoomScale(xRanges, yRanges):
        # Percent to zoom
        percent = .25
        xLen = abs(xRanges[1] - xRanges[0])
        yLen = abs(yRanges[1] - yRanges[0])
        xScale = (xLen * percent) / 2
        yScale = (yLen * percent) / 2
        return xScale, yScale

    def zoomOutTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        yRanges = self.roadGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.roadGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] + xScale)
        self.roadGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] + yScale)

    def zoomInTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        yRanges = self.roadGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.roadGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] - xScale)
        self.roadGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] - yScale)

    # TODO: Fix issue where graph is squished
    def jogLeftTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2

        self.roadGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] + xScale)

    # TODO: Fix issue where graph is squished
    def jogRightTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        scale = (abs(xRanges[0]) - abs(xRanges[1]) - (abs(xRanges[0]) - abs(xRanges[1])) * 0.75) / 2
        self.roadGraphWidget.setXRange(xRanges[0] - scale, xRanges[1] - scale)

    # TODO: Fix issue where graph is squished
    def jogUpTool(self):
        yRanges = self.roadGraphWidget.getAxis('left').range
        scale = (abs(yRanges[0]) - abs(yRanges[1]) - (abs(yRanges[0]) - abs(yRanges[1])) * 0.75) / 2
        self.roadGraphWidget.setYRange(yRanges[0] + scale, yRanges[1] + scale)

    # TODO: Fix issue where graph is squished
    def jogDownTool(self):
        yRanges = self.roadGraphWidget.getAxis('left').range
        scale = (abs(yRanges[0]) - abs(yRanges[1]) - (abs(yRanges[0]) - abs(yRanges[1])) * 0.75) / 2
        self.roadGraphWidget.setYRange(yRanges[0] - scale, yRanges[1] - scale)

    # Creates the navigation toolbar
    def __navToolbar(self):
        toolbar = QtWidgets.QToolBar("Navigation Toolbar")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(toolbar)
        # Zoom in
        zoom_in = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self)
        zoom_in.triggered.connect(self.zoomInTool)
        toolbar.addAction(zoom_in)
        # Zoom out
        zoom_out = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self)
        zoom_out.triggered.connect(self.zoomOutTool)
        toolbar.addAction(zoom_out)
        # Jog left
        jogLeft = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self)
        jogLeft.triggered.connect(self.jogLeftTool)
        toolbar.addAction(jogLeft)
        # Jog right
        jogRight = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self)
        jogRight.triggered.connect(self.jogRightTool)
        toolbar.addAction(jogRight)
        # Jog up
        jogUp = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self)
        jogUp.triggered.connect(self.jogUpTool)
        toolbar.addAction(jogUp)
        # Jog down
        jogDown = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-down-solid.svg'), "Jog Down", self)
        jogDown.triggered.connect(self.jogDownTool)
        toolbar.addAction(jogDown)

    def __menuBar(self):
        mainMenu = self.menuBar()
        # Add File menu option
        addFileMenu = mainMenu.addMenu("File")
        addFileAction = QtWidgets.QAction("Files", self)
        addFileAction.setShortcut("Ctrl+f")
        addFileAction.setStatusTip("View files")
        addFileAction.triggered.connect(self.viewFiles)
        addFileMenu.addAction(addFileAction)
        # Add View menu option
        addViewMenu = mainMenu.addMenu("View")
        viewSummaryAction = QtWidgets.QAction("Summary", self, checkable=True)
        viewSummaryAction.setStatusTip("View summary graphs")
        viewSummaryAction.triggered.connect(self.viewSummary)
        addViewMenu.addAction(viewSummaryAction)
        # Hide POIs button
        # hidePOIs = QtWidgets.QAction("Hide POIs", self, checkable=True, checked=True)
        # hidePOIs.setStatusTip("Hide POIs on the graph")
        # hidePOIs.triggered.connect(lambda: self.hidePOIs(hidePOIs.isChecked()))
        # addViewMenu.addAction(hidePOIs)
        networks = self.getCompleteNetworks()
        # Add Social Network option
        addSNMenu = mainMenu.addMenu("Social Network")
        # Loads all social networks available
        sNetworks = networks["Social Networks"]
        socialGroup = QtWidgets.QActionGroup(self)
        socialGroup.setExclusive(True)
        sActions = {"None": QtWidgets.QAction("None", self, checkable=True)}
        sActions["None"].setStatusTip(f"Display no social network")
        sActions["None"].triggered.connect(lambda junk: self.displaySocialNetwork(None))
        socialGroup.addAction(sActions["None"])
        # Adds all actions
        for x in sNetworks:
            sActions[x] = QtWidgets.QAction(x, self, checkable=True)
            sActions[x].setStatusTip(f"Switch to view social network {x}")
            sActions[x].triggered.connect(lambda junk, a=x: self.displaySocialNetwork(a))
            socialGroup.addAction(sActions[x])
        # Put actions in group and on menu
        addSNMenu.addActions(sActions.values())
        # Add Road Network option
        addRNMenu = mainMenu.addMenu("Road Network")
        # Loads all road networks available
        rNetworks = networks["Road Networks"]
        roadGroup = QtWidgets.QActionGroup(self)
        roadGroup.setExclusive(True)
        rActions = {"None": QtWidgets.QAction("None", self, checkable=True)}
        rActions["None"].setStatusTip(f"Display no road network")
        rActions["None"].triggered.connect(lambda junk: self.displayRoadNetwork(None))
        roadGroup.addAction(rActions["None"])
        # Adds all actions
        for x in rNetworks:
            rActions[x] = QtWidgets.QAction(x, self, checkable=True)
            rActions[x].setStatusTip(f"Switch to view road network {x}")
            rActions[x].triggered.connect(lambda junk, a=x: self.displayRoadNetwork(a))
            roadGroup.addAction(rActions[x])
        # Put actions in group and on menu
        addRNMenu.addActions(rActions.values())

    def clearView(self):
        self.win.removeItem(self.roadGraphWidget)
        if self.socialGraphWidget:
            self.win.removeItem(self.socialGraphWidget)
        if self.queryUserPlots:
            self.queryUserPlots = []
        self.roadGraphWidget = None
        self.socialGraphWidget = None

    # Returns users with at least k keywords in common (default to 1)
    def usersCommonKeyword(self, k=1):
        commonUsers = []
        commonDetails = {}
        if self.queryUser is not None:
            users = self.selectedSocialNetwork.getUsers()
            for user in users:
                if user is not self.queryUser[0]:
                    common = list(set(self.selectedSocialNetwork.getUserKeywords(user)).intersection(
                        self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])))
                    if len(common) > (k-1):
                        commonDetails[user] = common
                        commonUsers.append(user)
        return commonUsers, commonDetails

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

    def usersWithinHops(self, users, h=0):
        withinHops = []
        hopsDetails = {}
        for user in users:
            hops = self.selectedSocialNetwork.numberOfHops(self.queryUser[0], user)
            if h == 0:
                withinHops.append(user)
                hopsDetails[user] = hops
            else:
                if hops <= h and hops != -1:
                    withinHops.append(user)
                    hopsDetails[user] = hops
        return withinHops, hopsDetails

    # Returns users within d distance
    def usersWithinDistance(self, users, d=2):
        withinDistance = []
        distDetails = {}
        common = self.selectedSocialNetwork.userLoc(self.queryUser[0])
        commonLoc = self.selectedRoadNetwork.findNearest(common)
        for user in users:
            query = self.selectedSocialNetwork.userLoc(user)
            queryLoc = self.selectedRoadNetwork.findNearest(query)
            dist = self.selectedRoadNetwork.realUserDistance(queryLoc, commonLoc)
            if dist <= d:
                withinDistance.append(user)
                distDetails[user] = dist
        return withinDistance, distDetails

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
            self.sumLayout = QtWidgets.QHBoxLayout()
            self.sumLayout.addWidget(self.socialNetWidget, 50)
            self.sumLayout.addWidget(self.win, 50)
            self.view.setLayout(self.sumLayout)
            self.setCentralWidget(self.view)
            self.__clusterInput()
            self.__queryInput()
            self.updateSummaryGraph()
        # Switch view to main
        else:
            # Setup default view
            self.view = QtWidgets.QWidget()
            self.layout = QtWidgets.QHBoxLayout()
            self.layout.addWidget(self.win)
            self.view.setLayout(self.layout)
            self.setCentralWidget(self.view)
            self.summarySelected = False
            self.clusterInput.close()
            self.clearView()
            self.queryInput.close()
            self.createPlots()
            # Re-visualize selected networks
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.plotQueryUser()

    def visualizeSummaryData(self, centers, sizes, relations, popSize):
        # Note: For some reason, the alpha value is from 0-255 not 0-100
        self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                  symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
        self.plotQueryUser()
        # Create Interactive Graph HTML File Using pyvis
        network = nx.Graph()
        for i in range(0, len(centers)):
            network.add_node(str(centers[i][0]) + str(centers[i][1]), physics=False, label=popSize[i])
        for i in range(1, len(relations[0])):
            network.add_edge(str(relations[0][i]) + str(relations[1][i]),
                             str(relations[0][i - 1]) + str(relations[1][i - 1]))
        nt = Network('100%', '100%')
        nt.from_nx(network)
        nt.save_graph('nx.html')
        # LEGACY SOCIAL NETWORK GRAPH
        #self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
        #                            symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 150))
        #self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 100),
        #                            brush=(50, 50, 200, 100))

    def updateSummaryGraph(self):
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
            centers, sizes, relations, popSize = self.getSummaryClusters(self.clusterInput.textBox.text())
            self.visualizeSummaryData(centers, sizes, relations, popSize)
            with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)
        self.plotQueryUser()

    def visualizeKdData(self, users, keys, hops, dists):
        if self.queryUser is not None:
            # Create Interactive Graph HTML File Using pyvis
            network = nx.Graph()
            titleTemp = '<p>Keywords:</p><ol>'
            # Add query user
            queryKeys = self.selectedSocialNetwork.getUserKeywords(self.queryUser[0])
            for key in queryKeys:
                titleTemp += '<li>' + str(key) + '</li>'
            titleTemp += '</ol>'
            network.add_node(self.queryUser[0], physics=False, label=str('Query: ') + str(int(float(self.queryUser[0]))),
                             color='red', title=titleTemp)
            # Add common users
            common = self.selectedSocialNetwork.userLoc(self.queryUser[0])
            commonLoc = self.selectedRoadNetwork.findNearest(common)
            for user in users:
                query = self.selectedSocialNetwork.userLoc(user)
                d = dists[user]
                h = hops[user]
                k = keys[user]
                temp = '<p>Number of hops: ' + str(h) + '</p><p>Distance: ' + str(d) + '</p><p>Common Keywords:</p><ol>'
                for key in k:
                    temp += '<li>' + str(key) + '</li>'
                temp += '</ol>'
                network.add_node(user, physics=False, label=str(int(float(user))), color='blue', title=temp)
                rels = self.selectedSocialNetwork.commonRelations(user, users)
                for rel in rels:
                    network.add_edge(rel, user, color='blue')
            qu = self.queryUser[0]
            self.clearView()
            self.createSumPlot()
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            centers, sizes, relations, popSize = self.getSummaryClusters(self.clusterInput.textBox.text())
            self.visualizeSummaryData(centers, sizes, relations, popSize)
            self.setQueryUser(qu)
            self.plotQueryUser()
            for user in users:
                temp = self.selectedSocialNetwork.userLoc(user)
                self.roadGraphWidget.plot([float(temp[0][0])], [float(temp[0][1])], pen=None, symbol='o', symbolSize=10,
                                          symbolPen=(50, 50, 200, 25), symbolBrush=(50, 50, 200, 175))
                network.add_edge(self.queryUser[0], user, color='red')
            nt = Network('100%', '100%')
            nt.from_nx(network)
            nt.save_graph('nx.html')
    
    def updateKdSummaryGraph(self):
        self.socialNetWidget.reload()
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            kd, keys, hops, dists = self.getKDTrust(self.queryInput.kTextBox.text(), self.queryInput.dTextBox.text(),
                                 self.queryInput.eTextBox.text())
            self.visualizeKdData(kd, keys, hops, dists)
            with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)

    #Generate kdtrust from input
    def getKDTrust(self, keywords, distance, hops):
        if self.queryUser is not None:
            # Users with common keywords
            common, keys = self.usersCommonKeyword(k=float(keywords))
            # Narrow query down to users within hops
            common, hops = self.usersWithinHops(common, h=float(hops))
            # Narrow down with degree of similarity distance (longest compute time)
            common, dists = self.usersWithinDistance(common, d=float(distance))
            return common, keys, hops, dists

    # Generate clusters from the social network
    def getSummaryClusters(self, n):
        n = int(n)
        if n < 1:
            n = 10
        # n_clusters is th number of nodes to plot
        kmeans = KMeans(n_clusters=int(n))
        chunkedData = self.selectedSocialNetwork.getChunkedLocData()
        kmeans.fit(chunkedData)
        # Scales the nodes according to population
        centers = kmeans.cluster_centers_
        # Get items in clusters and put it into dictionary {'clusterid': [userid, userid...], ...}
        clusterItems = {}
        for i in range(0, len(chunkedData)):
            label = kmeans.labels_[i]
            userid = self.selectedSocialNetwork.getIDByLoc(chunkedData[i][0], chunkedData[i][1])
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

    # Returns size for cluster icons so that clusters that contain fewer nodes are smaller
    @staticmethod
    def sizeSort(refs):
        sizes = []
        refsSorted = refs.copy()
        refsSorted.sort()
        for x in refs:
            sizes += [((refsSorted.index(x) + 1) * (75 / len(refsSorted)))]
        return sizes

    def __queryUserButton(self):
        # Set up input toolbar
        self.queryUserToolbar = QtWidgets.QToolBar("queryUser")
        self.addToolBar(self.queryUserToolbar)
        # Create button
        button = QtWidgets.QPushButton("Select Query User")
        button.clicked.connect(lambda: self.chooseKeywordsMenu())
        button2 = QtWidgets.QPushButton("Select Query Keyword")
        button2.clicked.connect(lambda: self.chooseQueryKeywordMenu())
        # Create label
        label = QtWidgets.QLabel("  Query User: ")
        label2 = QtWidgets.QLabel("  Query Keyword: ")
        if self.queryUser is not None:
            self.queryUserToolbar.userLabel = QtWidgets.QLabel(self.queryUser[0].split(".0")[0])
        else:
            self.queryUserToolbar.userLabel = QtWidgets.QLabel("None")
        if self.queryKeyword is not None:
            self.queryUserToolbar.keywordLabel = QtWidgets.QLabel(self.queryKeyword)
        else:
            self.queryUserToolbar.keywordLabel = QtWidgets.QLabel("None")
        # Add widgets to window
        self.queryUserToolbar.addWidget(button)
        self.queryUserToolbar.addWidget(label)
        self.queryUserToolbar.addWidget(self.queryUserToolbar.userLabel)
        self.queryUserToolbar.addWidget(QtWidgets.QLabel("          "))
        self.queryUserToolbar.addWidget(button2)
        self.queryUserToolbar.addWidget(label2)
        self.queryUserToolbar.addWidget(self.queryUserToolbar.keywordLabel)

    def chooseKeywordsMenu(self):
        # Window setup
        self.__windows[3] = QtWidgets.QWidget()
        self.__windows[3].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[3].setWindowTitle('Choose Keywords')
        self.__windows[3].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        self.__windows[3].checkboxes = []
        # Checkboxes
        row = 0
        column = 0
        if self.selectedSocialNetwork is not None:
            for keyword in self.selectedSocialNetwork.getKeywords():
                widget = QtWidgets.QCheckBox(keyword)
                self.__windows[3].checkboxes.append(widget)
                layout.addWidget(widget, row, column)
                column += 1
                if column == 20:
                    column = 0
                    row += 1
            button = QtWidgets.QPushButton("Ok")
            button.clicked.connect(lambda: self.showUsersWithKeywords())
            layout.addWidget(button, row + 2, 19)
        else:
            button = QtWidgets.QPushButton("Cancel")
            button.clicked.connect(lambda: self.__windows[3].close())
            layout.addWidget(QtWidgets.QLabel("No Social Network Selected"), 0, 0)
            layout.addWidget(button, 1, 0)
        # Show QWidget
        self.__windows[3].setLayout(layout)
        self.__windows[3].show()
        self.__windows[3].move(self.geometry().center() - self.__windows[3].rect().center())

    def chooseQueryKeywordMenu(self):
        # Window setup
        self.__windows[5] = QtWidgets.QWidget()
        self.__windows[5].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[5].setWindowTitle('Choose Query Keyword')
        self.__windows[5].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        self.__windows[5].buttons = []
        # Buttons
        row = 0
        column = 0
        if self.queryUser is not None:
            for keyword in self.selectedSocialNetwork.getUserKeywords(self.queryUser[0]):
                widget = QtWidgets.QPushButton(keyword)
                widget.clicked.connect(lambda junk, k=keyword: self.setQueryKeyword(k))
                self.__windows[5].buttons.append(widget)
                layout.addWidget(widget, row, column)
                column += 1
                if column == 20:
                    column = 0
                    row += 1
        else:
            button = QtWidgets.QPushButton("Cancel")
            button.clicked.connect(lambda: self.__windows[5].close())
            layout.addWidget(QtWidgets.QLabel("No Query User Selected"), 0, 0)
            layout.addWidget(button, 1, 0)
        # Show QWidget
        self.__windows[5].setLayout(layout)
        self.__windows[5].show()
        self.__windows[5].move(self.geometry().center() - self.__windows[5].rect().center())

    def showUsersWithKeywords(self):
        checkboxes = self.__windows[3].checkboxes
        self.__windows[3].close()
        self.__windows[4] = QtWidgets.QWidget()
        self.__windows[4].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[4].setWindowTitle('Choose a Query User')
        self.__windows[4].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        keywords = []
        for checkbox in checkboxes:
            if checkbox.isChecked():
                keywords.append(checkbox.text())
        if len(keywords) == 0:
            self.__windows[4].close()
        else:
            users = self.selectedSocialNetwork.getUsersWithKeywords(keywords)
            row = 0
            column = 0
            for user in users:
                widget = QtWidgets.QPushButton(user.split(".0")[0])
                widget.clicked.connect(lambda junk, u=user: self.setQueryUser(u))
                layout.addWidget(widget, row, column)
                column += 1
                if column == 10:
                    column = 0
                    row += 1
            self.__windows[4].setLayout(layout)
            self.__windows[4].show()
            self.__windows[4].move(self.geometry().center() - self.__windows[4].rect().center())

    # Creates the cluster toolbar for input
    def __clusterInput(self):
        # Set up input toolbar
        self.clusterInput = QtWidgets.QToolBar("clusterInput")
        self.clusterInput.setIconSize(QtCore.QSize(24, 24))
        #self.keywordInput = QtWidgets.QToolBar("keyowrdInput")
        #self.keywordInput.setIconSize(QtCore.QSize(24, 24))
        #self.distanceInput = QtWidgets.QToolBar("distanceInput")
        #self.distanceInput.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(self.clusterInput)
        # Create labels
        nLabel = QtWidgets.QLabel(text="n-clusters: ")
        #kLabel = QtWidgets.QLabel(text="keywords: ")
        #dLabel = QtWidgets.QLabel(text="distance: ")
        # Create buttons
        button = QtWidgets.QPushButton("Ok")
        button.clicked.connect(lambda: self.updateSummaryGraph())
        # Create text boxs
        self.clusterInput.textBox = QtWidgets.QLineEdit()
        self.clusterInput.textBox.setValidator(QtGui.QIntValidator(0, 9999))
        self.clusterInput.textBox.setText("10")
        self.clusterInput.textBox.returnPressed.connect(button.click)
        #self.keywordInput.textBox = QtWidgets.QLineEdit()
        #self.keywordInput.textBox.setValidator(QtGui.QIntValidator(0, 9999))
        #self.keywordInput.textBox.setText("0")
        #self.keywordInput.textBox.returnPressed.connect(button.click)
        #self.distanceInput.textBox = QtWidgets.QLineEdit()
        #self.distanceInput.textBox.setValidator(QtGui.QIntValidator(0, 9999))
        #self.distanceInput.textBox.setText("0")
        #self.distanceInput.textBox.returnPressed.connect(button.click)
        # Add widgets to window
        self.clusterInput.addWidget(nLabel)
        self.clusterInput.addWidget(self.clusterInput.textBox)
        #self.clusterInput.addWidget(kLabel)
        #self.clusterInput.addWidget(self.keywordInput.textBox)
        #self.clusterInput.addWidget(dLabel)
        #self.clusterInput.addWidget(self.distanceInput.textBox)
        self.clusterInput.addWidget(button)

    # Returns query user in form [id, [[lat, lon], [lat, lon]]]
    def setQueryUser(self, user):
        if self.queryUser is not None:
            [a.clear() for a in self.queryUserPlots]
            self.queryUserPlots = []
        self.queryUser = self.selectedSocialNetwork.getUser(user)
        self.plotQueryUser()
        self.queryUserToolbar.userLabel.setText(user.split(".0")[0])
        self.usersCommonKeyword()
        self.__windows[4].close()
        self.dijkstra(self.queryUser)

    def plotQueryUser(self):
        if self.queryUser is not None:
            if not self.queryUserPlots:
                [a.clear() for a in self.queryUserPlots]
            self.queryUserPlots = []
            if self.summarySelected:
                color = (0, 255, 0)
            else:
                color = (255, 0, 0)
            for loc in self.queryUser[1]:
                self.queryUserPlots.append(self.roadGraphWidget.plot([float(loc[0])], [float(loc[1])], pen=None,
                                                                     symbol='star', symbolSize=30, symbolPen=color,
                                                                     symbolBrush=color))

    def setQueryKeyword(self, keyword):
        self.queryKeyword = keyword
        self.queryUserToolbar.keywordLabel.setText(keyword)
        self.__windows[5].close()

    def __queryInput(self):
        # Set up input toolbar
        self.queryInput = QtWidgets.QToolBar("queryInput")
        self.queryInput.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(self.queryInput)
        # Create label
        kLabel = QtWidgets.QLabel(text="  k: ")
        dLabel = QtWidgets.QLabel(text="  d: ")
        eLabel = QtWidgets.QLabel(text="  η: ")
        # Create button
        button = QtWidgets.QPushButton("Get Query")
        button.clicked.connect(lambda: self.updateKdSummaryGraph())
        # Create k text box
        self.queryInput.kTextBox = QtWidgets.QLineEdit()
        self.queryInput.kTextBox.setValidator(QtGui.QIntValidator(0, 9999))
        self.queryInput.kTextBox.setText("5")
        self.queryInput.kTextBox.returnPressed.connect(button.click)
        self.queryInput.kTextBox.setToolTip("k is used to control the community's structural cohesiveness. Larger k "
                                            "means higher structural cohesiveness")
        # Create d text box
        self.queryInput.dTextBox = QtWidgets.QLineEdit()
        self.queryInput.dTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
        self.queryInput.dTextBox.setText("1")
        self.queryInput.dTextBox.returnPressed.connect(button.click)
        self.queryInput.dTextBox.setToolTip("d controls the maximum number of hops between users")
        # Create e text box
        self.queryInput.eTextBox = QtWidgets.QLineEdit()
        self.queryInput.eTextBox.setValidator(QtGui.QIntValidator(0, 9999))
        self.queryInput.eTextBox.setText("0")
        self.queryInput.eTextBox.returnPressed.connect(button.click)
        self.queryInput.eTextBox.setToolTip("η controls the minimum degree of similarity between users")
        # Add widgets to window
        self.queryInput.addWidget(kLabel)
        self.queryInput.addWidget(self.queryInput.kTextBox)
        self.queryInput.addWidget(dLabel)
        self.queryInput.addWidget(self.queryInput.dTextBox)
        self.queryInput.addWidget(eLabel)
        self.queryInput.addWidget(self.queryInput.eTextBox)
        self.queryInput.addWidget(button)

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
                    "keyMapFile": "[keyMapFile]"
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
            self.linkGraphAxis()
        else:
            self.clearView()
            self.createPlots()
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            self.selectedRoadNetwork.visualize(None, self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.linkGraphAxis()

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
            self.linkGraphAxis()
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
                centers, sizes, relations, popSize = self.getSummaryClusters(self.clusterInput.textBox.text())
                self.visualizeSummaryData(centers, sizes, relations, popSize)
            self.plotQueryUser()
            #self.linkGraphAxis()

    def displaySocialNetwork(self, network):
        self.queryUser = None
        [a.clear() for a in self.queryUserPlots]
        self.queryUserPlots = []
        self.queryUserToolbar.userLabel.setText("None")
        self.queryKeyword = None
        self.queryUserToolbar.keywordLabel.setText("None")
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
            self.linkGraphAxis()
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
                centers, sizes, relations, popSize = self.getSummaryClusters(self.clusterInput.textBox.text())
                self.visualizeSummaryData(centers, sizes, relations, popSize)

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

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Closed")
        exit(0)
