from collections import Counter
from os.path import exists
from os import getenv

from matplotlib import interactive
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
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        screensize = self.screen().availableSize().width(), self.screen().availableSize().height()
        self.setGeometry(int((screensize[0] / 2) - 500), int((screensize[1] / 2) - 300), 1000, 600)
        self.setWindowTitle("Spatial-Social Network Graph")
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.graphView = QWebEngineView()

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
        # Stores selected network instances
        self.selectedRoadNetwork = None
        self.selectedSocialNetwork = None
        # Store data for interactive network
        self.interactiveNetwork = nx.Graph()
        # Store all network info in dict format {"NetworkName: {"Data": "Value", ...}, ..."}
        self.__roadNetworks = self.config.settings["Road Networks"]
        self.__socialNetworks = self.config.settings["Social Networks"]
        # Store network objects
        self.__roadNetworkObjs = self.createNetworkInstances(self.__roadNetworks, RoadNetwork)
        self.__socialNetworkObjs = self.createNetworkInstances(self.__socialNetworks, SocialNetwork)
        # Initializes menus
        self.__menuBar()
        self.__toolbar()
        self.__mainWindow()

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
        self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
        self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
        # Links the x and y-axis on both graphs
        self.linkGraphs()
        # Draw cross-hairs on graph
        self.drawSocialCrosshair()
        self.drawRoadCrosshair()
        # Adds event listener
        self.roadGraphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        # Show window
        self.show()

    def getZoomScale(self, xRanges, yRanges):
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
        scale = ((abs(xRanges[0]) - abs(xRanges[1])) - (abs(xRanges[0]) - abs(xRanges[1])) * 0.75) / 2
        self.roadGraphWidget.setXRange(xRanges[0] + scale, xRanges[1] + scale)

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
        print(self.selectedSocialNetwork)

    def __toolbar(self):
        toolbar = QtWidgets.QToolBar("My main toolbar")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(toolbar)
        zoom_in = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self)
        zoom_in.triggered.connect(self.zoomInTool)
        toolbar.addAction(zoom_in)
        zoom_out = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self)
        zoom_out.triggered.connect(self.zoomOutTool)
        toolbar.addAction(zoom_out)

        jogLeft = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self)
        jogLeft.triggered.connect(self.jogLeftTool)
        toolbar.addAction(jogLeft)

        jogRight = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self)
        jogRight.triggered.connect(self.jogRightTool)
        toolbar.addAction(jogRight)

        jogUp = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self)
        jogUp.triggered.connect(self.jogUpTool)
        toolbar.addAction(jogUp)

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

        # Add Social Network option
        addSNMenu = mainMenu.addMenu("Social Network")
        # Loads all social networks available
        # TODO: Look into toggle buttons for menu
        sNetworks = self.getCompleteSocialNetworks()
        sActions = {}
        for x in sNetworks:
            sActions[x] = QtWidgets.QAction(x, self, checkable=True)
            sActions[x].setStatusTip(f"Switch to view social network {x}")
            sActions[x].triggered.connect(lambda junk, a=x: self.displaySocialNetwork(a, sActions[a].isChecked()))
            addSNMenu.addAction(sActions[x])

        # Add Road Network option
        addRNMenu = mainMenu.addMenu("Road Network")
        # Loads all road networks available
        rNetworks = self.getCompleteRoadNetworks()
        rActions = {}
        for x in rNetworks:
            rActions[x] = QtWidgets.QAction(x, self, checkable=True)
            rActions[x].setStatusTip(f"Switch to view road network {x}")
            rActions[x].triggered.connect(lambda junk, a=x: self.displayRoadNetwork(a, rActions[a].isChecked()))
            addRNMenu.addAction(rActions[x])

    def viewInterNetwork(self, checked):
        self.netgwin = NetworkGraphWindow()
        self.netgwin.show()

    # Handles summary view
    def viewSummary(self):
        # TODO: Implement summary graph
        # Switch view to summary
        if not self.summarySelected:
            self.summarySelected = True
            # Clears last view
            self.win.removeItem(self.roadGraphWidget)
            self.win.removeItem(self.socialGraphWidget)
            # Displays summary plots
            self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
            self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
            self.__interactivePlotInput()
            self.__clusterInput()
            self.updateSummaryGraph()
        # Switch view to main
        else:
            self.summarySelected = False
            self.clusterInput.close()
            self.interactivePlotInput.close()
            self.win.removeItem(self.roadGraphWidget)
            self.win.removeItem(self.socialGraphWidget)
            self.roadGraphWidget = None
            self.socialGraphWidget = None
            self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
            self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
            # Re-visualize selected networks
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.drawRoadCrosshair()
            self.drawSocialCrosshair()
            self.linkGraphs()

    def updateSummaryGraph(self):
        # Clears last view
        if self.summarySelected:
            self.win.removeItem(self.roadGraphWidget)
            self.win.removeItem(self.socialGraphWidget)
        # Displays summary plots
        self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
        self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
        # Draw crosshairs on graph
        self.drawRoadSummaryCrosshair()
        self.drawSocialSummaryCrosshair()
        # Links the x and y axis on both graphs
        self.linkSummaryGraphs()
        # Adds event listener
        self.roadGraphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        # If a road network is selected, display info
        if self.selectedRoadNetwork is not None:
            self.selectedRoadNetwork.visualize(self.roadGraphWidget)
        # If social network is selected, display clusters
        if self.selectedSocialNetwork is not None:
            centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
            # Create Interactive Graph HTML File
            network = nx.Graph()
            for i in range(0, len(centers)):
                network.add_node(str(centers[i][0]) + str(centers[i][1]), physics=False)
            for i in range(1, len(relations[0])):
                network.add_edge(str(relations[0][i]) + str(relations[1][i]), str(relations[0][i-1]) +str(relations[1][i-1]))
            nt = Network('100%', '100%')
            nt.from_nx(network)
            nt.save_graph('nx.html')
            # Note: For some reason, the alpha value is from 0-255 not 0-100
            self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                                 symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
            self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
                                      symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
            self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 200),
                        brush=(50, 50, 200, 256))

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
        relations = [[],[]]
        while len(clusterStart) != 1:
            start = clusterStart[0]
            for item in clusterStart:
                if clusterStart[0] is not item:
                    relations[0].append(centers[start][0])
                    relations[0].append(centers[item][0])
                    relations[1].append(centers[start][1])
                    relations[1].append(centers[item][1])
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
            sizes.append((refsSorted.index(x) + 1) * (75 / len(refsSorted)))
        return sizes

    def __interactivePlotInput(self):
        self.interactivePlotInput = QtWidgets.QToolBar("interactivePlotInput")
        self.interactivePlotInput.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(self.interactivePlotInput)
        interactiveNet = QtWidgets.QAction(QtGui.QIcon('Assets/diagram-project-solid'), "Interactive Graph", self)
        interactiveNet.triggered.connect(self.viewInterNetwork)
        self.interactivePlotInput.addAction(interactiveNet)

    # Creates the cluster toolbar for input
    def __clusterInput(self):
        self.clusterInput = QtWidgets.QToolBar("clusterInput")
        self.clusterInput.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(self.clusterInput)
        label = QtWidgets.QLabel(text="n-clusters: ")
        self.clusterInput.textBox = QtWidgets.QLineEdit()
        self.clusterInput.textBox.setValidator(QtGui.QIntValidator(0, 9999))
        self.clusterInput.textBox.setText("10")
        button = QtWidgets.QPushButton("Ok")
        button.clicked.connect(lambda: self.updateSummaryGraph())
        self.clusterInput.addWidget(label)
        self.clusterInput.addWidget(self.clusterInput.textBox)
        self.clusterInput.addWidget(button)

    def viewFiles(self):
        self.__fileTreeObjects = {
            '0': QtWidgets.QTreeWidgetItem(["Road Networks"]),
            '1': QtWidgets.QTreeWidgetItem(["Social Networks"])
        }
        self.__windows[0] = pg.TreeWidget()
        # Settings for TreeWidget
        self.__windows[0].setWindowModality(QtCore.Qt.ApplicationModal)
        self.__windows[0].setDragEnabled(False)
        self.__windows[0].header().setSectionsMovable(False)
        self.__windows[0].header().setStretchLastSection(False)
        self.__windows[0].header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.__windows[0].setWindowTitle('Files')
        self.__windows[0].setColumnCount(2)
        self.__windows[0].resize(int(self.frameGeometry().width() / 3), int(self.frameGeometry().height() / 3))
        # Show TreeWidget
        self.__windows[0].show()
        # Add Road Networks and Social Networks to hierarchy
        self.__windows[0].addTopLevelItem(self.__fileTreeObjects['0'])
        self.__windows[0].addTopLevelItem(self.__fileTreeObjects['1'])
        # Add button to add a new Road Network
        nrn = QtWidgets.QPushButton("New Road Network")
        nrn.clicked.connect(self.newRoadNetwork)
        self.__windows[0].setItemWidget(self.__fileTreeObjects['0'], 1, nrn)
        # Add button to add a new Social Network
        nsn = QtWidgets.QPushButton("New Social Network")
        nsn.clicked.connect(self.newSocialNetwork)
        self.__windows[0].setItemWidget(self.__fileTreeObjects['1'], 1, nsn)
        # Adds all sub-objects to roadNetworks
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
                if self.__roadNetworks[x][y] != f"[{self.__roadNetworks[x][y]}]":
                    iNameArr = self.__roadNetworks[x][y].split("/")
                    iName = iNameArr[len(iNameArr) - 1]
                self.__fileTreeObjects[f"0.{i}.{j}"] = QtWidgets.QTreeWidgetItem([iName])
                self.__fileTreeObjects[f"0.{i}"].addChild(self.__fileTreeObjects[f"0.{i}.{j}"])
                cFile[j] = QtWidgets.QPushButton("Choose File")
                cFile[j].clicked.connect(
                    lambda junk, a=i, d=j, b=x, c=y: self.chooseFile(f"0.{a}.{d}", "Road Network", b, c))
                self.__windows[0].setItemWidget(self.__fileTreeObjects[f"0.{i}.{j}"], 1, cFile[j])
        # Adds all sub-objects to socialNetworks
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
                if self.__socialNetworks[x][y] != f"[{self.__socialNetworks[x][y]}]":
                    iNameArr = self.__socialNetworks[x][y].split("/")
                    iName = iNameArr[len(iNameArr) - 1]
                self.__fileTreeObjects[f"1.{i}.{j}"] = QtWidgets.QTreeWidgetItem([iName])
                self.__fileTreeObjects[f"1.{i}"].addChild(self.__fileTreeObjects[f"1.{i}.{j}"])
                cFileS[f"{j}.{j}"] = QtWidgets.QPushButton("Choose File")
                cFileS[f"{j}.{j}"].clicked.connect(
                    lambda junk, a=i, b=j, c=x, d=y: self.chooseFile(f"1.{a}.{b}", "Social Network", c, d))
                self.__windows[0].setItemWidget(self.__fileTreeObjects[f"1.{i}.{j}"], 1, cFileS[f"{j}.{j}"])

    def newRoadNetwork(self):
        self.__windows[1] = QtWidgets.QInputDialog()
        text, ok = self.__windows[1].getText(self, 'New Road Network', "Enter your road network name:")
        if ok and str(text) not in self.__roadNetworks.keys() and str(text) != "":
            self.__roadNetworks[str(text)] = {
                "nodeFile": "[nodeFile]",
                "edgeFile": "[edgeFile]"
            }
            # Adds new road network to tree
            self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}"] = QtWidgets.QTreeWidgetItem([str(text)])
            self.__fileTreeObjects['0'].addChild(self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}"])
            # Adds new road network's node file
            self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}.1"] = \
                QtWidgets.QTreeWidgetItem([self.__roadNetworks[str(text)]["nodeFile"]])
            self.__fileTreeObjects[f'0.{len(self.__roadNetworks.keys()) + 1}'].addChild(
                self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}.1"])
            addN = QtWidgets.QPushButton("Choose File")
            addN.clicked.connect(
                lambda: self.chooseFile(f"0.{len(self.__roadNetworks.keys()) + 1}.1", "Road Network", str(text),
                                        "nodeFile"))
            self.__windows[0].setItemWidget(self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}.1"], 1, addN)
            # Adds new road network's edge file
            self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"] = \
                QtWidgets.QTreeWidgetItem([self.__roadNetworks[str(text)]["edgeFile"]])
            self.__fileTreeObjects[f'0.{len(self.__roadNetworks.keys()) + 1}'].addChild(
                self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"])
            addE = QtWidgets.QPushButton("Choose File")
            addE.clicked.connect(lambda: self.chooseFile(f"0.{len(self.__roadNetworks.keys()) + 1}.2", "Road Network", str(text),
                                        "Edge File"))
            self.__windows[0].setItemWidget(self.__fileTreeObjects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"], 1, addE)
            # Update config
            self.config.update("Road Networks", self.__roadNetworks)

    def newSocialNetwork(self):
        self.__windows[1] = QtWidgets.QInputDialog()
        text, ok = self.__windows[1].getText(self, 'New Social Network', "Enter your social network name:")
        if ok and str(text) not in self.__socialNetworks.keys() and str(text) != "":
            self.__socialNetworks[str(text)] = {
                "locFile": "[locFile]",
                "relFile": "[relFile]",
                "keyFile": "[keyFile]"
            }
            # Adds new social network to tree
            self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}"] = QtWidgets.QTreeWidgetItem([str(text)])
            self.__fileTreeObjects['1'].addChild(self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}"])
            # Adds new social network's loc file
            self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.1"] = \
                QtWidgets.QTreeWidgetItem([self.__socialNetworks[str(text)]["locFile"]])
            self.__fileTreeObjects[f'1.{len(self.__socialNetworks.keys()) + 1}'].addChild(
                self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.1"])
            addL = QtWidgets.QPushButton("Choose File")
            addL.clicked.connect(
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.1", "Social Network", str(text),
                                        "Loc File"))
            self.__windows[0].setItemWidget(self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.1"], 1, addL)
            # Adds new social network's rel file
            self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.2"] = \
                QtWidgets.QTreeWidgetItem([self.__socialNetworks[str(text)]["relFile"]])
            self.__fileTreeObjects[f'1.{len(self.__socialNetworks.keys()) + 1}'].addChild(
                self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.2"])
            addR = QtWidgets.QPushButton("Choose File")
            addR.clicked.connect(
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.2", "Social Network", str(text),
                                        "Rel File"))
            self.__windows[0].setItemWidget(self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.2"], 1, addR)
            # Adds new social network's key file
            self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.3"] = \
                QtWidgets.QTreeWidgetItem([self.__socialNetworks[str(text)]["keyFile"]])
            self.__fileTreeObjects[f'1.{len(self.__socialNetworks.keys()) + 1}'].addChild(
                self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.3"])
            addR = QtWidgets.QPushButton("Choose File")
            addR.clicked.connect(
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.1", "Social Network", str(text),
                                        "Key File"))
            self.__windows[0].setItemWidget(self.__fileTreeObjects[f"1.{len(self.__socialNetworks.keys()) + 1}.3"], 1, addR)
            # Update config
            self.config.update("Social Networks", self.__socialNetworks)
            self.menuBar().clear()
            self.__menuBar()

    def chooseFile(self, obj, T, network, sub):
        self.__windows[2] = QtWidgets.QFileDialog()
        pathArr = self.__windows[2].getOpenFileNames(None, 'Select File', getenv('HOME'), "csv(*.csv)")[0]
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
    def getCompleteRoadNetworks(self):
        networks = []
        for x in self.__roadNetworks:
            if self.__roadNetworks[x]["edgeFile"] != "[Edge File]" and \
                    exists(self.__roadNetworks[x]["edgeFile"]) and \
                    self.__roadNetworks[x]["nodeFile"] != "[nodeFile]" and \
                    exists(self.__roadNetworks[x]["nodeFile"]):
                networks.append(x)
        return networks

    # Return social networks that have all files and those files exist
    def getCompleteSocialNetworks(self):
        networks = []
        for x in self.__socialNetworks:
            if self.__socialNetworks[x]["relFile"] != "[relFile]" and \
                    exists(self.__socialNetworks[x]["relFile"]) and \
                    self.__socialNetworks[x]["locFile"] != "[locFile]" and \
                    exists(self.__socialNetworks[x]["locFile"]):
                networks.append(x)
        return networks

    def displayRoadNetwork(self, network, checked=None):
        if not self.summarySelected:
            if checked:
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.win.removeItem(self.roadGraphWidget)
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # If there is a social network selected, remove and re-add to make sure nodes stay above the plot
                if self.selectedSocialNetwork is not None:
                    # Visualize
                    self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
                # Visualizes the graph that is being selected
                self.__roadNetworkObjs[network].visualize(self.roadGraphWidget)
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
            else:
                # Removes the widget and re-adds it to be blank
                self.win.removeItem(self.roadGraphWidget)
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                self.selectedRoadNetwork = None
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                # Removes the social network and re-adds it to keep the graph there
                if self.selectedSocialNetwork is not None:
                    self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
            self.drawSocialCrosshair()
            self.drawRoadCrosshair()
            self.linkGraphs()
        else:
            if checked:
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                self.win.removeItem(self.roadGraphWidget)
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
                self.selectedRoadNetwork.visualize(self.roadGraphWidget)
                # If there is a social network selected, remove and re-add to make sure nodes stay above the plot
                if self.selectedSocialNetwork is not None:
                    centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
                    # Note: For some reason, the alpha value is from 0-255 not 0-100
                    self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                                     symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                    self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
                                                symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                    self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 200),
                                                brush=(50, 50, 200, 256))
                self.linkSummaryGraphs()
                # Draw crosshairs on graph
                self.drawRoadSummaryCrosshair()
                self.drawSocialSummaryCrosshair()
            else:
                # Removes the widget and re-adds it to be blank
                self.win.removeItem(self.roadGraphWidget)
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                self.selectedRoadNetwork = None
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                # Removes the social network and re-adds it to keep the graph there
                if self.selectedSocialNetwork is not None:
                    centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
                    # Note: For some reason, the alpha value is from 0-255 not 0-100
                    self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                                     symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                    self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
                                                symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                    self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 200),
                                                brush=(50, 50, 200, 256))
            # Draw crosshairs on graph
            self.drawRoadSummaryCrosshair()
            self.drawSocialSummaryCrosshair()
            # Links the x and y axis on both graphs
            self.socialGraphWidget.setXLink(self.roadGraphWidget)
            self.socialGraphWidget.setYLink(self.roadGraphWidget)

    def displaySocialNetwork(self, network, checked=None):
        # If main view
        if not self.summarySelected:
            if checked:
                # Visualizes social network
                self.__socialNetworkObjs[network].visualize(self.socialGraphWidget, self.roadGraphWidget)
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
            else:
                # Removes both graphs to clear them then re-adds them
                self.win.removeItem(self.socialGraphWidget)
                self.win.removeItem(self.roadGraphWidget)
                self.selectedSocialNetwork = None
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # Re-visualizes the road network if it is selected
                if self.selectedRoadNetwork:
                    self.selectedRoadNetwork.visualize(self.roadGraphWidget)
                # Draw crosshairs on graph
                self.drawSocialCrosshair()
                self.drawRoadCrosshair()
                self.socialGraphWidget.setXLink(self.roadGraphWidget)
                self.socialGraphWidget.setYLink(self.roadGraphWidget)
        # If summary view
        else:
            if checked:
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
                self.win.removeItem(self.socialGraphWidget)
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                self.win.removeItem(self.roadGraphWidget)
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                if self.selectedRoadNetwork is not None:
                    self.selectedRoadNetwork.visualize(self.roadGraphWidget)
                centers, sizes, relations = self.getSummaryClusters(self.clusterInput.textBox.text())
                # Note: For some reason, the alpha value is from 0-255 not 0-100
                self.roadGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=sizes,
                                          symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                self.socialGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=20,
                                            symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                self.socialGraphWidget.plot(relations[0], relations[1], connect='pairs', pen=(50, 50, 200, 200),
                                            brush=(50, 50, 200, 256))
                self.linkSummaryGraphs()
                # Draw crosshairs on graph
                self.drawRoadSummaryCrosshair()
                self.drawSocialSummaryCrosshair()
            else:
                # Removes both graphs to clear them then re-adds them
                self.win.removeItem(self.socialGraphWidget)
                self.win.removeItem(self.roadGraphWidget)
                self.selectedSocialNetwork = None
                self.socialGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.roadGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # Re-visualizes the road network if it is selected
                if self.selectedRoadNetwork:
                    self.selectedRoadNetwork.visualize(self.roadGraphWidget)
                # Draw crosshairs on graph
                self.drawRoadSummaryCrosshair()
                self.drawSocialSummaryCrosshair()
                self.linkSummaryGraphs()

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

    def drawSocialCrosshair(self):
        # Draw crosshairs on graph
        self.socialGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False, pen=(140, 130, 10, 50))
        self.socialGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False, pen=(140, 130, 10, 50))
        self.socialGraphWidget.addItem(self.socialGraphWidget.vCrossLine, ignoreBounds=True)
        self.socialGraphWidget.addItem(self.socialGraphWidget.hCrossLine, ignoreBounds=True)

    def drawRoadCrosshair(self):
        # Draw crosshairs on graph
        self.roadGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False, pen=(140, 130, 10, 50))
        self.roadGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False, pen=(140, 130, 10, 50))
        self.roadGraphWidget.addItem(self.roadGraphWidget.vCrossLine, ignoreBounds=True)
        self.roadGraphWidget.addItem(self.roadGraphWidget.hCrossLine, ignoreBounds=True)

    def drawSocialSummaryCrosshair(self):
        # Draw crosshairs on graph
        self.socialGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False, pen=(140, 130, 10, 50))
        self.socialGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False, pen=(140, 130, 10, 50))
        self.socialGraphWidget.addItem(self.socialGraphWidget.vCrossLine, ignoreBounds=True)
        self.socialGraphWidget.addItem(self.socialGraphWidget.hCrossLine, ignoreBounds=True)

    def drawRoadSummaryCrosshair(self):
        # Draw crosshairs on graph
        self.roadGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False, pen=(140, 130, 10, 50))
        self.roadGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False, pen=(140, 130, 10, 50))
        self.roadGraphWidget.addItem(self.roadGraphWidget.vCrossLine, ignoreBounds=True)
        self.roadGraphWidget.addItem(self.roadGraphWidget.hCrossLine, ignoreBounds=True)

    # Links X and Y axis on summary social network and main network graphs
    def linkSummaryGraphs(self):
        self.socialGraphWidget.setXLink(self.roadGraphWidget)
        self.socialGraphWidget.setYLink(self.roadGraphWidget)

    # Links X and Y axis on main social network and road network graphs
    def linkGraphs(self):
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
