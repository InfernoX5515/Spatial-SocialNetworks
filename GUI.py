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
from local.KDTrust import KDTrust


# Menu bar class for more simple management
class MenuBar:
    def __init__(self, menuBar):
        self.menu = menuBar
        self.menuTree = Node('root')
        self.__menuGroups = {}

    def addMenu(self, name):
        menu = self.menu.addMenu(name)
        Node(name, obj=menu, parent=self.menuTree)

    def addChild(self, name, parent, shortcut=None, tooltip=None, action=None, group=None, checked=False):
        child = QtWidgets.QAction(name, self.menu)

        if shortcut is not None:
            child.setShortcut(shortcut)
        if tooltip is not None:
            child.setStatusTip(tooltip)
        if action is not None:
            child.triggered.connect(action)
        if group is not None:
            if group not in self.__menuGroups:
                raise Exception(f"Group '{group}' does not exist.")
            self.__menuGroups[group].addAction(child)
            child.setCheckable(True)
            child.setChecked(checked)

        parentNode = find_by_attr(self.menuTree, parent)
        if parentNode is None:
            raise Exception(f"Menu item '{parent}' was not found.")
        parentNode.obj.addAction(child)
        Node(name, obj=child, parent=parentNode)

    def createGroup(self, name, appRoot):
        if name in self.__menuGroups:
            raise Exception(f"Group '{name}' already exists.")
        self.__menuGroups[name] = QtWidgets.QActionGroup(appRoot)

    def printTree(self):
        print(RenderTree(self.menuTree))


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
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(0)
        self.sumLayout = QtWidgets.QGridLayout(self)
        self.sumLayout.setSpacing(0)
        self.view = QtWidgets.QWidget()
        # Initializes menus
        self.__menuBar()
        #self.__navToolbar()
        self.__queryUserButton()
        self.__mainWindow()
        # Array for plot points
        self.centers = []
        self.ids = []

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
            self.showClusterUsers(self.selectedSocialNetwork.getClusterUsers(self.ids[closest_point]))

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
        self.__navToolbar()
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

    def jogLeftTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.roadGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] - xScale, padding=0)

    def jogRightTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.roadGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] + xScale, padding=0)

    def jogUpTool(self):
        yRanges = self.roadGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.roadGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] + yScale, padding=0)

    def jogDownTool(self):
        yRanges = self.roadGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.roadGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] - yScale, padding=0)



    def zoomOutToolSocial(self):
        xRanges = self.socialGraphWidget.getAxis('bottom').range
        yRanges = self.socialGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.socialGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] + xScale)
        self.socialGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] + yScale)

    def zoomInToolSocial(self):
        xRanges = self.socialGraphWidget.getAxis('bottom').range
        yRanges = self.socialGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.socialGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] - xScale)
        self.socialGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] - yScale)

    def jogLeftToolSocial(self):
        xRanges = self.socialGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.socialGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] - xScale, padding=0)

    def jogRightToolSocial(self):
        xRanges = self.socialGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.socialGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] + xScale, padding=0)

    def jogUpToolSocial(self):
        yRanges = self.socialGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.socialGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] + yScale, padding=0)

    def jogDownToolSocial(self):
        yRanges = self.socialGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.socialGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] - yScale, padding=0)

    def zoomInToolInteractive(self):
        self.socialNetWidget.page().runJavaScript(r"network.moveTo({scale: network.getScale()+0.2});")

    def zoomOutToolInteractive(self):
        self.socialNetWidget.page().runJavaScript(r"network.moveTo({scale: network.getScale()-0.2});")

    def jogUpToolInteractive(self):
        self.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x'], y:t['y']-20}});")

    def jogDownToolInteractive(self):
        self.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x'], y:t['y']+20}});")

    def jogRightToolInteractive(self):
        self.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x']+20, y:t['y']}});")

    def jogLeftToolInteractive(self):
        self.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x']-20, y:t['y']}});")

    # Creates the navigation toolbar
    def __navToolbar(self):
        # Create toolbar for road graph
        toolbar = QtWidgets.QToolBar("Navigation Toolbar")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        #self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)
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
        if self.summarySelected:
            self.sumLayout.addWidget(toolbar, 1, 1)
            # Create a second toolbar for the social graph
            socialToolbar = QtWidgets.QToolBar("Navigation Toolbar")
            socialToolbar.setIconSize(QtCore.QSize(24, 24))
            #self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)
            # Zoom in
            zoom_in_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self)
            zoom_in_social.triggered.connect(self.zoomInToolInteractive)
            socialToolbar.addAction(zoom_in_social)
            # Zoom out
            zoom_out_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self)
            zoom_out_social.triggered.connect(self.zoomOutToolInteractive)
            socialToolbar.addAction(zoom_out_social)
            # Jog left
            jogLeft_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self)
            jogLeft_social.triggered.connect(self.jogLeftToolInteractive)
            socialToolbar.addAction(jogLeft_social)
            # Jog right
            jogRight_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self)
            jogRight_social.triggered.connect(self.jogRightToolInteractive)
            socialToolbar.addAction(jogRight_social)
            # Jog up
            jogUp_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self)
            jogUp_social.triggered.connect(self.jogUpToolInteractive)
            socialToolbar.addAction(jogUp_social)
            # Jog down
            jogDown_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-down-solid.svg'), "Jog Down", self)
            jogDown_social.triggered.connect(self.jogDownToolInteractive)
            socialToolbar.addAction(jogDown_social)

            self.sumLayout.addWidget(socialToolbar, 1, 0)
        else:
            # Add the toolbar to the road graph
            self.layout.addWidget(toolbar, 1, 1)
            # Create a second toolbar for the social graph
            socialToolbar = QtWidgets.QToolBar("Navigation Toolbar")
            socialToolbar.setIconSize(QtCore.QSize(24, 24))
            #self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)
            # Zoom in
            zoom_in_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self)
            zoom_in_social.triggered.connect(self.zoomInToolSocial)
            socialToolbar.addAction(zoom_in_social)
            # Zoom out
            zoom_out_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self)
            zoom_out_social.triggered.connect(self.zoomOutToolSocial)
            socialToolbar.addAction(zoom_out_social)
            # Jog left
            jogLeft_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self)
            jogLeft_social.triggered.connect(self.jogLeftToolSocial)
            socialToolbar.addAction(jogLeft_social)
            # Jog right
            jogRight_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self)
            jogRight_social.triggered.connect(self.jogRightToolSocial)
            socialToolbar.addAction(jogRight_social)
            # Jog up
            jogUp_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self)
            jogUp_social.triggered.connect(self.jogUpToolSocial)
            socialToolbar.addAction(jogUp_social)
            # Jog down
            jogDown_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-down-solid.svg'), "Jog Down", self)
            jogDown_social.triggered.connect(self.jogDownToolSocial)
            socialToolbar.addAction(jogDown_social)
            self.layout.addWidget(socialToolbar, 1, 0)
        
        
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

        menu.addMenu("Query")
        menu.addChild("kd-truss", "Query", tooltip="kd-truss menu", action=self.__queryInput)

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
            self.sumLayout = QtWidgets.QGridLayout()
            
            self.sumLayout.setSpacing(0)
            self.sumLayout.addWidget(self.socialNetWidget, 0, 0, 2,1)
            self.sumLayout.addWidget(self.win, 0, 1)
            self.sumLayout.setColumnStretch(0, 1)
            self.sumLayout.setColumnStretch(1, 1)
            self.__navToolbar()
            self.view.setLayout(self.sumLayout)
            self.setCentralWidget(self.view)
            self.__clusterInput()
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
            self.__navToolbar()
            self.view.setLayout(self.layout)
            self.setCentralWidget(self.view)
            self.clusterInput.close()
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
            self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.clusterInput.textBox.text())
            self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
            with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)
        self.plotQueryUser()


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
            nt = Network('100%', '100%')
            nt.from_nx(graph)
            nt.save_graph('kd-trust.html')






            qu = self.queryUser[0]
            self.clearView()
            self.createSumPlot()
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.clusterInput.textBox.text())
            self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
            self.setQueryUser(qu)
            

            for user in result_users:
                temp = self.selectedSocialNetwork.userLoc(user)
                self.roadGraphWidget.plot([float(temp[0][0])], [float(temp[0][1])], pen=None, symbol='o', symbolSize=10,
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
            kdTree = self.getKDTrust(self.__windows[6].kTextBox.text(), self.__windows[6].dTextBox.text(),
                                 self.__windows[6].eTextBox.text())
            self.visualizeKdData(kdTree)
            with open('kd-trust.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)


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
                if column == 10:
                    column = 0
                    row += 1
            button = QtWidgets.QPushButton("Ok")
            button.clicked.connect(lambda: self.showUsersWithKeywords())
            layout.addWidget(button, row + 2, 8)
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
                widget = QtWidgets.QPushButton(self.selectedSocialNetwork.getKeywordByID(keyword))
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

    def __showUserInfo(self, listWidget, name, username, birthdate, email, phone, keywordList, userList):
        name.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["name"])
        username.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["username"])
        birthdate.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["birthdate"])
        email.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["email"])
        phone.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["phone"])
        keywordString = ""
        for id in self.selectedSocialNetwork.getUserKeywords(userList[listWidget.currentRow()]):
            keywordString += self.selectedSocialNetwork.getKeywordByID(id) + "\n"
        keywordList.setText(keywordString)

    def showUsersWithKeywords(self):
        checkboxes = self.__windows[3].checkboxes
        self.__windows[3].close()
        self.__windows[4] = QtWidgets.QWidget()
        self.__windows[4].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[4].setWindowTitle('Choose a Query User')
        self.__windows[4].resize(int(self.frameGeometry().width()), int(self.frameGeometry().height()))
        mainLayout = QtWidgets.QVBoxLayout(self)
        scroll = QtWidgets.QScrollArea(self)
        self.__windows[4].setLayout(mainLayout)
        mainLayout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scrollContent = QtWidgets.QWidget(scroll)
        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(2, 2)
        scrollContent.setLayout(layout)
        keywords = []
        for checkbox in checkboxes:
            if checkbox.isChecked():
                keywords.append(self.selectedSocialNetwork.getIDByKeyword(checkbox.text()))
        if len(keywords) == 0:
            self.__windows[4].close()
        else:
            users = self.selectedSocialNetwork.getUsersWithKeywords(keywords)
            row = 0
            column = 0
            headingFont=QtGui.QFont()
            headingFont.setBold(True)
            headingFont.setPointSize(18)
            BoldLabel=QtGui.QFont()
            BoldLabel.setBold(True)
            listWidget = QtWidgets.QListWidget()
            keywordList = QtWidgets.QLabel()
            userHeading = QtWidgets.QLabel("Users:")
            userHeading.setFixedHeight(20)
            userHeading.setFont(headingFont)
            detailHeading = QtWidgets.QLabel("User Details:")
            detailHeading.setFixedHeight(20)
            detailHeading.setFont(headingFont)
            keywordHeading = QtWidgets.QLabel("User Keywords:")
            keywordHeading.setFont(headingFont)
            keywordHeading.setFixedHeight(20)
            nameLabel = QtWidgets.QLabel("Name: ")
            nameLabel.setFont(BoldLabel)
            nameLabel.setFixedHeight(16)
            name = QtWidgets.QLabel()
            usernameLabel = QtWidgets.QLabel("Username: ")
            usernameLabel.setFixedHeight(16)
            usernameLabel.setFont(BoldLabel)
            username = QtWidgets.QLabel()
            birthdateLabel = QtWidgets.QLabel("Birthdate: ")
            birthdateLabel.setFont(BoldLabel)
            birthdateLabel.setFixedHeight(16)
            birthdate = QtWidgets.QLabel()
            emailLabel = QtWidgets.QLabel("Email: ")
            emailLabel.setFont(BoldLabel)
            emailLabel.setFixedHeight(16)
            email = QtWidgets.QLabel()
            phoneLabel = QtWidgets.QLabel("Phone: ")
            phoneLabel.setFont(BoldLabel)
            phoneLabel.setFixedHeight(16)
            phone = QtWidgets.QLabel()
            setQueryUsr = QtWidgets.QPushButton("Set as Query User")
            setQueryUsr.clicked.connect(lambda: self.setQueryUser(userList[listWidget.currentRow()]))
            userList = []
            for user in users:
                userList.append(user)
                listWidget.addItem(self.selectedSocialNetwork.getUserAttributes(user)["name"] + " (" + user.split(".0")[0] + ")")
                

            listWidget.itemSelectionChanged.connect(lambda: self.__showUserInfo(listWidget, name, username, birthdate, email, phone, keywordList, userList))
            layout.addWidget(userHeading, 0, 0)
            layout.addWidget(detailHeading, 0, 1, 1, 2)
            layout.addWidget(listWidget, 1, 0, 7, 1)
            layout.addWidget(nameLabel, 1, 1)
            layout.addWidget(name, 1, 2)
            layout.addWidget(usernameLabel, 2, 1)
            layout.addWidget(username, 2, 2)
            layout.addWidget(birthdateLabel, 3, 1)
            layout.addWidget(birthdate, 3, 2)
            layout.addWidget(emailLabel, 4, 1)
            layout.addWidget(email, 4, 2)
            layout.addWidget(phoneLabel, 5, 1)
            layout.addWidget(phone, 5, 2)
            layout.addWidget(keywordHeading, 6, 1, 1, 2)
            layout.addWidget(keywordList, 7, 1, 1, 2)
            keywordList.setAlignment(QtCore.Qt.AlignTop)
            layout.addWidget(setQueryUsr, 8, 0, 1, 3)
            scroll.setWidget(scrollContent)
            self.__windows[4].show()
            self.__windows[4].move(self.geometry().center() - self.__windows[4].rect().center())

    def showClusterUsers(self, users):
        self.__windows[7] = QtWidgets.QWidget()
        self.__windows[7].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[7].setWindowTitle('Cluster Users')
        self.__windows[7].resize(int(self.frameGeometry().width()), int(self.frameGeometry().height()))

        mainLayout = QtWidgets.QVBoxLayout(self)
        scroll = QtWidgets.QScrollArea(self)
        self.__windows[7].setLayout(mainLayout)
        mainLayout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scrollContent = QtWidgets.QWidget(scroll)
        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(2, 2)
        scrollContent.setLayout(layout)

        headingFont=QtGui.QFont()
        headingFont.setBold(True)
        headingFont.setPointSize(18)
        BoldLabel=QtGui.QFont()
        BoldLabel.setBold(True)
        listWidget = QtWidgets.QListWidget()
        keywordList = QtWidgets.QLabel()
        userHeading = QtWidgets.QLabel("Users:")
        userHeading.setFixedHeight(20)
        userHeading.setFont(headingFont)
        detailHeading = QtWidgets.QLabel("User Details:")
        detailHeading.setFixedHeight(20)
        detailHeading.setFont(headingFont)
        keywordHeading = QtWidgets.QLabel("User Keywords:")
        keywordHeading.setFont(headingFont)
        keywordHeading.setFixedHeight(20)
        nameLabel = QtWidgets.QLabel("Name: ")
        nameLabel.setFont(BoldLabel)
        nameLabel.setFixedHeight(16)
        name = QtWidgets.QLabel()
        usernameLabel = QtWidgets.QLabel("Username: ")
        usernameLabel.setFixedHeight(16)
        usernameLabel.setFont(BoldLabel)
        username = QtWidgets.QLabel()
        birthdateLabel = QtWidgets.QLabel("Birthdate: ")
        birthdateLabel.setFont(BoldLabel)
        birthdateLabel.setFixedHeight(16)
        birthdate = QtWidgets.QLabel()
        emailLabel = QtWidgets.QLabel("Email: ")
        emailLabel.setFont(BoldLabel)
        emailLabel.setFixedHeight(16)
        email = QtWidgets.QLabel()
        phoneLabel = QtWidgets.QLabel("Phone: ")
        phoneLabel.setFont(BoldLabel)
        phoneLabel.setFixedHeight(16)
        phone = QtWidgets.QLabel()
        setQueryUsr = QtWidgets.QPushButton("Set as Query User")
        closeWindow = QtWidgets.QPushButton("Close")
        setQueryUsr.clicked.connect(lambda: self.setQueryUser(userList[listWidget.currentRow()], window=7))
        closeWindow.clicked.connect(lambda: self.__windows[7].close())
        userList = []
        for user in users:
            userList.append(user)
            listWidget.addItem(self.selectedSocialNetwork.getUserAttributes(user)["name"] + " (" + user.split(".0")[0] + ")")
            

        listWidget.itemSelectionChanged.connect(lambda: self.__showUserInfo(listWidget, name, username, birthdate, email, phone, keywordList, userList))
        layout.addWidget(userHeading, 0, 0)
        layout.addWidget(detailHeading, 0, 1, 1, 2)
        layout.addWidget(listWidget, 1, 0, 7, 1)
        layout.addWidget(nameLabel, 1, 1)
        layout.addWidget(name, 1, 2)
        layout.addWidget(usernameLabel, 2, 1)
        layout.addWidget(username, 2, 2)
        layout.addWidget(birthdateLabel, 3, 1)
        layout.addWidget(birthdate, 3, 2)
        layout.addWidget(emailLabel, 4, 1)
        layout.addWidget(email, 4, 2)
        layout.addWidget(phoneLabel, 5, 1)
        layout.addWidget(phone, 5, 2)
        layout.addWidget(keywordHeading, 6, 1, 1, 2)
        layout.addWidget(keywordList, 7, 1, 1, 2)
        keywordList.setAlignment(QtCore.Qt.AlignTop)
        layout.addWidget(setQueryUsr, 8, 0, 1, 3)
        layout.addWidget(closeWindow, 9, 0, 1, 3)
        scroll.setWidget(scrollContent)







        self.__windows[7].show()
        self.__windows[7].move(self.geometry().center() - self.__windows[7].rect().center())


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
    def setQueryUser(self, user, window=4):
        if self.queryUser is not None:
            [a.clear() for a in self.queryUserPlots]
            self.queryUserPlots = []
        self.queryUser = self.selectedSocialNetwork.getUser(user)
        self.plotQueryUser()
        self.queryUserToolbar.userLabel.setText(user.split(".0")[0])
        self.usersCommonKeyword()
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
                self.clusterInput.textBox.text())
           self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
           with open('nx.html', 'r') as f:
                html = f.read()
                self.socialNetWidget.setHtml(html)


    def setQueryKeyword(self, keyword):
        self.queryKeyword = keyword
        self.queryUserToolbar.keywordLabel.setText(self.selectedSocialNetwork.getKeywordByID(keyword))
        self.__windows[5].close()

    def __queryInput(self):
        # Window setup
        self.__windows[6] = QtWidgets.QWidget()
        self.__windows[6].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[6].setWindowTitle('Query: kd-truss')
        self.__windows[6].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        # Set up input toolbar
        #self.queryInput = QtWidgets.QToolBar("queryInput")
        #self.queryInput.setIconSize(QtCore.QSize(24, 24))
        #self.addToolBar(self.queryInput)
        if self.queryUser is not None and self.summarySelected and self.selectedRoadNetwork is not None and self.selectedSocialNetwork is not None:
            # Create label
            kLabel = QtWidgets.QLabel(text="community's structural cohesiveness(k): ")
            dLabel = QtWidgets.QLabel(text="maximum number of hops(d): ")
            eLabel = QtWidgets.QLabel(text="minimum degree of similarity(η): ")
            # Create button
            button = QtWidgets.QPushButton("Get Query")
            button.clicked.connect(lambda: self.updateKdSummaryGraph())
            button.clicked.connect(lambda: self.__windows[6].close())
            # Create k text box
            self.__windows[6].kTextBox = QtWidgets.QSpinBox()
            self.__windows[6].kTextBox.setRange(1, 9999)
            self.__windows[6].kTextBox.setValue(3)
            self.__windows[6].kTextBox.setToolTip(
                "k is used to control the community's structural cohesiveness. Larger k means higher structural cohesiveness")
            # Create d text box
            self.__windows[6].dTextBox = QtWidgets.QLineEdit()
            self.__windows[6].dTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.__windows[6].dTextBox.setText("5")
            self.__windows[6].dTextBox.returnPressed.connect(button.click)
            self.__windows[6].dTextBox.setToolTip("d controls the maximum number of hops between users")
            # Create e text box
            self.__windows[6].eTextBox = QtWidgets.QLineEdit()
            self.__windows[6].eTextBox.setValidator(QtGui.QIntValidator(0, 9999))
            self.__windows[6].eTextBox.setText("0")
            self.__windows[6].eTextBox.returnPressed.connect(button.click)
            self.__windows[6].eTextBox.setToolTip("η controls the minimum degree of similarity between users")
            # Add widgets to window
            layout.addWidget(kLabel)
            layout.addWidget(self.__windows[6].kTextBox)
            layout.addWidget(dLabel)
            layout.addWidget(self.__windows[6].dTextBox)
            layout.addWidget(eLabel)
            layout.addWidget(self.__windows[6].eTextBox)
            layout.addWidget(button)
        else:
            if self.selectedSocialNetwork is None:
                noSocialLabel = QtWidgets.QLabel(text="No Social Network is selected.")
                # Add widgets to window
                layout.addWidget(noSocialLabel)
            if self.selectedRoadNetwork is None:
                noRoadLabel = QtWidgets.QLabel(text="No Road Network is selected.")
                # Add widgets to window
                layout.addWidget(noRoadLabel)
            if self.queryUser is None:
                noUserLabel = QtWidgets.QLabel(text="No Query User is selected.")
                # Add widgets to window
                layout.addWidget(noUserLabel)
            if not self.summarySelected:
                noSummaryLabel = QtWidgets.QLabel(text="Summary View is not selected.")
                # Add widgets to window
                layout.addWidget(noSummaryLabel)


        # Show QWidget
        self.__windows[6].setLayout(layout)
        self.__windows[6].show()
        self.__windows[6].move(self.geometry().center() - self.__windows[6].rect().center())

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
                    "userDataFile": "[userDataFile]"
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
                self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.clusterInput.textBox.text())
                self.visualizeSummaryData(self.ids, self.centers, sizes, relations, popSize)
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
                self.ids, self.centers, sizes, relations, popSize = self.selectedSocialNetwork.getSummaryClusters(self.clusterInput.textBox.text())
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

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Closed")
        exit(0)
