from collections import Counter
from os.path import exists
from os import getenv
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
# import time
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

class NetworkGraphWindow(QtWidgets.QWidget):

    #
    # Proof of Concept
    #

    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        screensize = self.screen().availableSize().width(), self.screen().availableSize().height()
        self.setGeometry(int((screensize[0] / 2) - 500), int((screensize[1] / 2) - 300), 1000, 600)
        self.setWindowTitle("Spatial-Social Network Graph")
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.graphView = QWebEngineView()
        network = nx.Graph()
        network.add_node(0)
        network.add_node(1)
        network.add_node(2)
        network.add_node(3)
        network.add_node(4)
        network.add_node(5)
        network.add_edge(0, 1)
        network.add_edge(0, 2)
        network.add_edge(0, 3)
        network.add_edge(4, 1)
        network.add_edge(5, 1)
        network.add_edge(5, 2)

        nt = Network('500px', '500px')

        nt.from_nx(network)
        nt.show('nx.html')
        with open('nx.html', 'r') as f:
            html = f.read()
            self.graphView.setHtml(html)
        layout.addWidget(self.graphView)
        self.setLayout(layout)


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
        self.summarySelected = False
        self.hidePOIsSelected = False
        # Stores selected network instances
        self.selectedRoadNetwork = None
        self.selectedSocialNetwork = None
        # Store all network info in dict format {"NetworkName: {"Data": "Value", ...}, ..."}
        self.__roadNetworks = self.config.settings["Road Networks"]
        self.__socialNetworks = self.config.settings["Social Networks"]
        # Store network objects
        self.__roadNetworkObjs = self.createNetworkInstances(self.__roadNetworks, RoadNetwork)
        self.__socialNetworkObjs = self.createNetworkInstances(self.__socialNetworks, SocialNetwork)
        # Initializes menus
        self.__menuBar()
        self.__navToolbar()
        self.__mainWindow()

    # Creates the plot widgets. suffix is used when a summary graph is created, for example
    def createPlots(self, suffix=None):
        self.roadGraphWidget = self.win.addPlot(row=0, col=1, title=f"Road Network {suffix}")
        self.socialGraphWidget = self.win.addPlot(row=0, col=0, title=f"Social Network {suffix}")
        self.linkGraphAxis()

    # Displays main window
    def __mainWindow(self):
        # Set up window
        screensize = self.screen().availableSize().width(), self.screen().availableSize().height()
        self.setGeometry(int((screensize[0] / 2) - 500), int((screensize[1] / 2) - 300), 1000, 600)
        self.setWindowTitle("Spatial-Social Networks")
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.win)
        # Create and set up graph widget
        self.createPlots()
        # Draw cross-hairs on graph
        self.drawCrosshairs()
        # Adds event listener
        self.roadGraphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
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
        yRanges = self.roadGraphWidget.getAxis('left').range
        #xScale, yScale = self.getZoomScale(xRanges, yRanges)
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2

        self.roadGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] - xScale)

    # TODO: Fix issue where graph is squished
    def jogRightTool(self):
        xRanges = self.roadGraphWidget.getAxis('bottom').range
        scale = ((abs(xRanges[0]) - abs(xRanges[1]) - ((abs(xRanges[0]) - abs(xRanges[1]))) * 0.75)) / 2
        self.roadGraphWidget.setXRange(xRanges[0] - scale, xRanges[1] - scale)

    # TODO: Fix issue where graph is squished
    def jogUpTool(self):
        yRanges = self.roadGraphWidget.getAxis('left').range
        scale = ((abs(yRanges[0]) - abs(yRanges[1]) - ((abs(yRanges[0]) - abs(yRanges[1]))) * 0.75)) / 2
        self.roadGraphWidget.setYRange(yRanges[0] + scale, yRanges[1] + scale)

    # TODO: Fix issue where graph is squished
    def jogDownTool(self):
        yRanges = self.roadGraphWidget.getAxis('left').range
        scale = ((abs(yRanges[0]) - abs(yRanges[1]) - ((abs(yRanges[0]) - abs(yRanges[1]))) * 0.75)) / 2
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
        # Interactive network button
        viewInterNetworkAction = QtWidgets.QAction("Interactive Network", self, checkable=True)
        viewInterNetworkAction.setStatusTip("Launch interactive network interface")
        viewInterNetworkAction.triggered.connect(self.viewInterNetwork)
        addViewMenu.addAction(viewInterNetworkAction)
        # Hide POIs button
        hidePOIs = QtWidgets.QAction("Hide POIs", self, checkable=True)
        hidePOIs.setStatusTip("Hide POIs on the graph")
        hidePOIs.triggered.connect(self.hidePOIs)
        addViewMenu.addAction(hidePOIs)
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
        print(rNetworks)
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

    def viewInterNetwork(self, checked):
        self.netgwin = NetworkGraphWindow()
        self.netgwin.show()

    def clearView(self):
        self.win.removeItem(self.roadGraphWidget)
        self.win.removeItem(self.socialGraphWidget)
        self.roadGraphWidget = None
        self.socialGraphWidget = None

    # Handles summary view
    def viewSummary(self):
        # Switch view to summary
        if not self.summarySelected:
            self.summarySelected = True
            self.clearView()
            # Displays summary plots
            self.createPlots("Summary")
            self.__clusterInput()
            self.updateSummaryGraph()
        # Switch view to main
        else:
            self.summarySelected = False
            self.clusterInput.close()
            self.clearView()
            self.createPlots()
            # Re-visualize selected networks
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.drawCrosshairs()

    def visualizeSummaryData(self, centers, sizes, relations):
        # Note: For some reason, the alpha value is from 0-255 not 0-100
        self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                  symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
        self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
                                    symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 150))
        self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 100),
                                    brush=(50, 50, 200, 100))

    def updateSummaryGraph(self):
        # Clears last view
        if self.summarySelected:
            self.clearView()
        self.createPlots("Summary")
        # Adds event listener
        self.roadGraphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        # If a road network is selected, display info
        if self.selectedRoadNetwork is not None:
            self.selectedRoadNetwork.visualize(self.roadGraphWidget)
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
            self.visualizeSummaryData(centers, sizes, relations)
        self.drawCrosshairs()

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
        return centers, sizes, relations

    # Returns size for cluster icons so that clusters that contain fewer nodes are smaller
    @staticmethod
    def sizeSort(refs):
        sizes = []
        refsSorted = refs.copy()
        refsSorted.sort()
        for x in refs:
            sizes += [((refsSorted.index(x) + 1) * (75 / len(refsSorted)))]
        return sizes

    # Creates the cluster toolbar for input
    def __clusterInput(self):
        # Set up input toolbar
        self.clusterInput = QtWidgets.QToolBar("clusterInput")
        self.clusterInput.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(self.clusterInput)
        # Create label
        label = QtWidgets.QLabel(text="n-clusters: ")
        # Create button
        button = QtWidgets.QPushButton("Ok")
        button.clicked.connect(lambda: self.updateSummaryGraph())
        # Create text box
        self.clusterInput.textBox = QtWidgets.QLineEdit()
        self.clusterInput.textBox.setValidator(QtGui.QIntValidator(0, 9999))
        self.clusterInput.textBox.setText("10")
        self.clusterInput.textBox.returnPressed.connect(button.click)
        # Add widgets to window
        self.clusterInput.addWidget(label)
        self.clusterInput.addWidget(self.clusterInput.textBox)
        self.clusterInput.addWidget(button)

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
                    "POIFile": "[POIFile]"
                }
            elif type == "social":
                network[text] = {
                    "locFile": "[locFile]",
                    "relFile": "[relFile]",
                    "keyFile": "[keyFile]"
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
                addN.clicked.connect(lambda: self.chooseFile(f"{num}.{currItem}.{i}", f"{title}", text,
                                                             f"{keys[i - 1]}"))
                self.__windows[0].setItemWidget(self.__fileTreeObjects[f"{num}.{currItem}.{i}"], 1, addN)
            # Update config
            self.config.update(f"{title}", network)

    def hidePOIs(self):
        print("test")

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
        if not self.summarySelected:
            self.clearView()
            self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
            self.selectedRoadNetwork = None
            self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
            # Removes the social network and re-adds it to keep the graph there
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            if network is not None:
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # If there is a social network selected, remove and re-add to make sure nodes stay above the plot
                if self.selectedSocialNetwork is not None:
                    # Visualize
                    self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
                # Visualizes the graph that is being selected
                self.__roadNetworkObjs[network].visualize(self.roadGraphWidget)
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
            self.drawCrosshairs()
        else:
            # Removes the widget and re-adds it to be blank
            self.clearView()
            self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
            self.selectedRoadNetwork = None
            self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
            # Removes the social network and re-adds it to keep the graph there
            if self.selectedSocialNetwork is not None:
                centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
                self.visualizeSummaryData(centers, sizes, relations)
            if network is not None:
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
                # If there is a social network selected, remove and re-add to make sure nodes stay above the plot
                if self.selectedSocialNetwork is not None:
                    centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
                    self.visualizeSummaryData(centers, sizes, relations)
                # Draw crosshairs on graph
                self.drawCrosshairs()
            # Draw crosshairs on graph
            self.drawCrosshairs()
            # Links the x and y axis on both graphs
            self.socialGraphWidget.setXLink(self.roadGraphWidget)
            self.socialGraphWidget.setYLink(self.roadGraphWidget)

    def displaySocialNetwork(self, network):
        # If main view
        if not self.summarySelected:
            # Removes both graphs to clear them then re-adds them
            self.clearView()
            self.selectedSocialNetwork = None
            self.createPlots()
            # Re-visualizes the road network if it is selected
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            self.drawCrosshairs()
            self.socialGraphWidget.setXLink(self.roadGraphWidget)
            self.socialGraphWidget.setYLink(self.roadGraphWidget)
            if network is not None:
                # Visualizes social network
                self.__socialNetworkObjs[network].visualize(self.socialGraphWidget, self.roadGraphWidget)
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
        # If summary view
        else:
            # Removes both graphs to clear them then re-adds them
            self.clearView()
            self.selectedSocialNetwork = None
            self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
            self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
            # Re-visualizes the road network if it is selected
            if self.selectedRoadNetwork:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            # Draw crosshairs on graph
            self.drawCrosshairs()
            if network is not None:
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                if self.selectedRoadNetwork is not None:
                    self.selectedRoadNetwork.visualize(self.roadGraphWidget)
                centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
                self.visualizeSummaryData(centers, sizes, relations)
                self.drawCrosshairs()

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

    def drawCrosshairs(self):
        # Draw social network cross-hairs
        self.socialGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False, pen=(140, 130, 10, 50))
        self.socialGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False, pen=(140, 130, 10, 50))
        self.socialGraphWidget.addItem(self.socialGraphWidget.vCrossLine, ignoreBounds=True)
        self.socialGraphWidget.addItem(self.socialGraphWidget.hCrossLine, ignoreBounds=True)
        # Draw Road network cross-hairs
        self.roadGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False, pen=(140, 130, 10, 50))
        self.roadGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False, pen=(140, 130, 10, 50))
        self.roadGraphWidget.addItem(self.roadGraphWidget.vCrossLine, ignoreBounds=True)
        self.roadGraphWidget.addItem(self.roadGraphWidget.hCrossLine, ignoreBounds=True)

    # Links X and Y axis on main social network and road network graphs
    def linkGraphAxis(self):
        self.socialGraphWidget.setXLink(self.roadGraphWidget)
        self.socialGraphWidget.setYLink(self.roadGraphWidget)

    # OnMouseMoved event
    def mouseMoved(self, evt):
        # Sets the mousePoint to whichever graph the pointer is over
        # roadGraphWidget
        if self.roadGraphWidget.sceneBoundingRect().contains(evt.x(), evt.y()):
            mousePoint = self.roadGraphWidget.vb.mapSceneToView(evt)
        else:
            if self.roadGraphWidget is not None:
                # socialGraphWidget
                if self.socialGraphWidget.sceneBoundingRect().contains(evt.x(), evt.y()):
                    mousePoint = self.socialGraphWidget.vb.mapSceneToView(evt)
                # roadGraphWidget
                else:
                    mousePoint = self.roadGraphWidget.vb.mapSceneToView(evt)
            # socialGraphWidget
            else:
                mousePoint = self.socialGraphWidget.vb.mapSceneToView(evt)
        if mousePoint is not None:
            if self.roadGraphWidget is None:
                # Moves the road network crosshair
                self.roadGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.roadGraphWidget.hCrossLine.setPos(mousePoint.y())
                # Moves the social network crosshair
                self.socialGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.socialGraphWidget.hCrossLine.setPos(mousePoint.y())
            else:
                # Moves the road network crosshair
                self.roadGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.roadGraphWidget.hCrossLine.setPos(mousePoint.y())
                # Moves the social network crosshair
                self.socialGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.socialGraphWidget.hCrossLine.setPos(mousePoint.y())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Closed")
        exit(0)
