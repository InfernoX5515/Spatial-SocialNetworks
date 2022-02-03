import ctypes
import platform
from collections import Counter
from Config import Config
from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import PyQt5.QtWidgets as QtWidgets
import os
from RoadNetwork import RoadNetwork
from SocialNetwork import SocialNetwork
from sklearn.cluster import KMeans


# =====================================================================================================================
#
#   Author: Halie Eckert
#   Date: 11/3/2021
#   Project: Spatial-Social Networks
#
#   Purpose:
#       GUI.py is the main class for the GUI. This class handles all guis, sub guis, variables, and object needed
#    to display data.
#
# =====================================================================================================================


class Gui(QtWidgets.QMainWindow):
    # TODO: Prevent clicking off sub-windows
    def __init__(self):
        super(Gui, self).__init__()
        self.config = Config()
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'white')

        #self.setWindowModality(QtCore.Qt.ApplicationModal)
        # A dictionary of windows, each window has it's on id
        self.__windows = {}
        # Used for storing all road network info
        self.__roadNetworks = self.config.settings["Road Networks"]
        self.__roadNetworkObjs = {}
        self.getRoadNetworkInstances()
        # Used for storing all social network info
        self.__socialNetworks = self.config.settings["Social Networks"]
        self.__socialNetworkObjs = {}
        self.getSocialNetworkInstances()
        # Used for storing file hierarchy data
        self.__objects = {}
        self.roadNetworkGraphWidget = None
        self.socialNetworkGraphWidget = None
        self.summaryGraphWidget = None
        self.selectedRealNetwork = None
        self.selectedSocialNetwork = None
        self.__menuBar()
        self.__toolbar()
        self.__mainWindow()

    def __mainWindow(self):
        # screensize = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)
        screensize = self.screen().availableSize().width(), self.screen().availableSize().height()
        self.setGeometry((screensize[0] / 2) - 500, (screensize[1] / 2) - 300, 1000, 600)
        self.setWindowTitle("Spatial-Social Networks")
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.win)
        self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
        self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
        self.show()

    def cursorTool(self):
        self.roadNetworkGraphWidget.setMouseEnabled(x=True, y=True)

    def zoomOutTool(self):
        #self.roadNetworkGraphWidget.setMouseEnabled(x=False, y=False)
        xRanges = self.roadNetworkGraphWidget.getAxis('bottom').range
        yRanges = self.roadNetworkGraphWidget.getAxis('left').range
        self.roadNetworkGraphWidget.setXRange(xRanges[0] - 0.5, xRanges[1] + 0.5)
        self.roadNetworkGraphWidget.setYRange(yRanges[0] - 0.5, yRanges[1] + 0.5)


    def zoomInTool(self):
        
        #self.roadNetworkGraphWidget.viewRange =  [[-124.8716955920008 + (-124.8716955920008 * .5), -113.81190540799919 - (-113.81190540799919 * 0.5)], [32.08680962346822 + (32.08680962346822 * 0.5), 42.47730737653178 - (42.47730737653178 * .5)]]
        #self.roadNetworkGraphWidget.setXRange((self.roadNetworkGraphWidget.viewRange[0][0] * 1.75) +  self.roadNetworkGraphWidget.viewRange[0][0],  self.roadNetworkGraphWidget.viewRange[0][1] - (self.roadNetworkGraphWidget.viewRange[0][1] * 1.75))
        xRanges = self.roadNetworkGraphWidget.getAxis('bottom').range
        yRanges = self.roadNetworkGraphWidget.getAxis('left').range
        self.roadNetworkGraphWidget.setXRange(xRanges[0] + 0.5, xRanges[1] - 0.5)
        self.roadNetworkGraphWidget.setYRange(yRanges[0] + 0.5, yRanges[1] - 0.5)

    def moveTool(self):
        self.roadNetworkGraphWidget.setMouseEnabled(x=False, y=False)

    def __toolbar(self):
        toolbar = QtWidgets.QToolBar("My main toolbar")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        self.addToolBar(toolbar)


        #cursor = QtWidgets.QAction(QtGui.QIcon('Assets/cursor.png'), "Cursor", self)
        #cursor.triggered.connect(self.cursorTool)
        #toolbar.addAction(cursor)

        zoom_in = QtWidgets.QAction(QtGui.QIcon('Assets/zoom-in.png'), "Zoom In", self)
        zoom_in.triggered.connect(self.zoomInTool)
        toolbar.addAction(zoom_in)

        zoom_out = QtWidgets.QAction(QtGui.QIcon('Assets/zoom-out.png'), "Zoom Out", self)
        zoom_out.triggered.connect(self.zoomOutTool)
        toolbar.addAction(zoom_out)

        #move = QtWidgets.QAction(QtGui.QIcon('Assets/move.png'), "Move", self)
        #move.triggered.connect(self.moveTool)
        #toolbar.addAction(move)






    def __menuBar(self):
        # TODO: Make check boxes only clear graph not entire plot
        self.statusBar()
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
        # Add Real Network option
        addRNMenu = mainMenu.addMenu("Road Network")
        # Loads all road networks available
        # TODO: Look into toggle buttons for menu
        rNetworks = self.getCompleteRoadNetworks()
        rActions = {}
        for x in rNetworks:
            rActions[x] = QtWidgets.QAction(x, self, checkable=True)
            rActions[x].setStatusTip(f"Switch to view road network {x}")
            rActions[x].triggered.connect(lambda junk, a=x: self.displayRoadNetwork(a, rActions[a].isChecked()))
            addRNMenu.addAction(rActions[x])

    def viewSummary(self):
        # TODO: Implement summary view
        # TODO: error handling when none
        # TODO: add user defined value for kmeans
        self.win.removeItem(self.roadNetworkGraphWidget)
        self.win.removeItem(self.socialNetworkGraphWidget)
        self.summaryGraphWidget = self.win.addPlot(row=0, col=1, title="Summary")
        self.selectedRealNetwork.visualize(self.summaryGraphWidget)
        # Draws summary nodes on graph. n_clusters is th number of nodes to plot
        # TODO: Add user-defined n_cluster amount
        kmeans = KMeans(n_clusters=int(10))
        kmeans.fit(self.selectedSocialNetwork.getChunkedLocData())
        # Scales the nodes according to population
        centers = kmeans.cluster_centers_
        ref = list(Counter(kmeans.labels_).values())
        refSorted = list(Counter(kmeans.labels_).values())
        refSorted.sort()
        # TODO: Make a better size sorting algorithm
        '''sizes = [0] * len(centers[:, 1])
        for z in range(0, len(refSorted)):
            for q in range(0, len(ref)):
                if int(ref[q]) == int(refSorted[z]):
                    sizes[q] = refSorted[z] / 5'''
        # Note: For some reason, the alpha value is from 0-255 not 0-100
        self.summaryGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=30,
                                     symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))

    def viewFiles(self):
        self.__objects = {
            '0': QtWidgets.QTreeWidgetItem(["Road Networks"]),
            '1': QtWidgets.QTreeWidgetItem(["Social Networks"])
        }
        # TODO: Prevent drag-drop
        # TODO: Scale window better
        # TODO: Have window open on top
        self.__windows[0] = pg.TreeWidget()
        self.__windows[0].header().setStretchLastSection(False)
        self.__windows[0].header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.__windows[0].setWindowTitle('Files')
        self.__windows[0].setColumnCount(2)
        self.__windows[0].show()
        # Add Road Networks and Social Networks to hierarchy
        self.__windows[0].addTopLevelItem(self.__objects['0'])
        self.__windows[0].addTopLevelItem(self.__objects['1'])
        # Add button to add a new Road Network
        nrn = QtWidgets.QPushButton("New Road Network")
        nrn.clicked.connect(self.newRoadNetwork)
        self.__windows[0].setItemWidget(self.__objects['0'], 1, nrn)
        # Add button to add a new Social Network
        nsn = QtWidgets.QPushButton("New Social Network")
        nsn.clicked.connect(self.newSocialNetwork)
        self.__windows[0].setItemWidget(self.__objects['1'], 1, nsn)
        # Adds all sub-objects to roadNetworks
        i = 0
        for x in self.__roadNetworks:
            i += 1
            self.__objects[f"0.{i}"] = QtWidgets.QTreeWidgetItem([x])
            self.__objects['0'].addChild(self.__objects[f"0.{i}"])
            j = 0
            # Adds files
            cFile = {}
            for y in self.__roadNetworks[x]:
                j += 1
                iName = self.__roadNetworks[x][y]
                if self.__roadNetworks[x][y] != f"[{self.__roadNetworks[x][y]}]":
                    iNameArr = self.__roadNetworks[x][y].split("/")
                    iName = iNameArr[len(iNameArr) - 1]
                self.__objects[f"0.{i}.{j}"] = QtWidgets.QTreeWidgetItem([iName])
                self.__objects[f"0.{i}"].addChild(self.__objects[f"0.{i}.{j}"])
                cFile[j] = QtWidgets.QPushButton("Choose File")
                cFile[j].clicked.connect(
                    lambda junk, a=i, d=j, b=x, c=y: self.chooseFile(f"0.{a}.{d}", "Road Network", b, c))
                self.__windows[0].setItemWidget(self.__objects[f"0.{i}.{j}"], 1, cFile[j])
        # Adds all sub-objects to socialNetworks
        i = 0
        cFileS = {}
        for x in self.__socialNetworks:
            i += 1
            self.__objects[f"1.{i}"] = QtWidgets.QTreeWidgetItem([x])
            self.__objects['1'].addChild(self.__objects[f"1.{i}"])
            j = 0
            # Adds files
            for y in self.__socialNetworks[x]:
                j += 1
                iName = self.__socialNetworks[x][y]
                if self.__socialNetworks[x][y] != f"[{self.__socialNetworks[x][y]}]":
                    iNameArr = self.__socialNetworks[x][y].split("/")
                    iName = iNameArr[len(iNameArr) - 1]
                self.__objects[f"1.{i}.{j}"] = QtWidgets.QTreeWidgetItem([iName])
                self.__objects[f"1.{i}"].addChild(self.__objects[f"1.{i}.{j}"])
                cFileS[f"{j}.{j}"] = QtWidgets.QPushButton("Choose File")
                cFileS[f"{j}.{j}"].clicked.connect(
                    lambda junk, a=i, b=j, c=x, d=y: self.chooseFile(f"1.{a}.{b}", "Social Network", c, d))
                self.__windows[0].setItemWidget(self.__objects[f"1.{i}.{j}"], 1, cFileS[f"{j}.{j}"])

    def newRoadNetwork(self):
        # TODO: Add exceptions, add error messages
        self.__windows[1] = QtWidgets.QInputDialog()
        text, ok = self.__windows[1].getText(self, 'New Road Network', "Enter your road network name:")
        if ok and str(text) not in self.__roadNetworks.keys() and str(text) != "":
            self.__roadNetworks[str(text)] = {
                "Node File": "[Node File]",
                "Edge File": "[Edge File]"
            }
            # Adds new road network to tree
            self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}"] = QtWidgets.QTreeWidgetItem([str(text)])
            self.__objects['0'].addChild(self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}"])
            # Adds new road network's node file
            self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.1"] = \
                QtWidgets.QTreeWidgetItem([self.__roadNetworks[str(text)]["Node File"]])
            self.__objects[f'0.{len(self.__roadNetworks.keys()) + 1}'].addChild(
                self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.1"])
            addN = QtWidgets.QPushButton("Choose File")
            addN.clicked.connect(
                lambda: self.chooseFile(f"0.{len(self.__roadNetworks.keys()) + 1}.1", "Road Network", str(text),
                                        "Node File"))
            self.__windows[0].setItemWidget(self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.1"], 1, addN)
            # Adds new road network's edge file
            self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"] = \
                QtWidgets.QTreeWidgetItem([self.__roadNetworks[str(text)]["Edge File"]])
            self.__objects[f'0.{len(self.__roadNetworks.keys()) + 1}'].addChild(
                self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"])
            addE = QtWidgets.QPushButton("Choose File")
            addE.clicked.connect(lambda: self.chooseFile(f"0.{len(self.__roadNetworks.keys()) + 1}.2", "Road Network", str(text),
                                        "Edge File"))
            self.__windows[0].setItemWidget(self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"], 1, addE)
            # Update config
            self.config.update("Road Networks", self.__roadNetworks)

    def newSocialNetwork(self):
        # TODO: Add exceptions, add error messages
        # TODO: When new social network/road network is created, refresh menus
        self.__windows[1] = QtWidgets.QInputDialog()
        text, ok = self.__windows[1].getText(self, 'New Social Network', "Enter your social network name:")
        if ok and str(text) not in self.__socialNetworks.keys() and str(text) != "":
            self.__socialNetworks[str(text)] = {
                "Loc File": "[Loc File]",
                "Rel File": "[Rel File]",
                "Key File": "[Key File]"
            }
            # Adds new social network to tree
            self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}"] = QtWidgets.QTreeWidgetItem([str(text)])
            self.__objects['1'].addChild(self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}"])
            # Adds new social network's loc file
            self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.1"] = \
                QtWidgets.QTreeWidgetItem([self.__socialNetworks[str(text)]["Loc File"]])
            self.__objects[f'1.{len(self.__socialNetworks.keys()) + 1}'].addChild(
                self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.1"])
            addL = QtWidgets.QPushButton("Choose File")
            addL.clicked.connect(
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.1", "Social Network", str(text),
                                        "Loc File"))
            self.__windows[0].setItemWidget(self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.1"], 1, addL)
            # Adds new social network's rel file
            self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.2"] = \
                QtWidgets.QTreeWidgetItem([self.__socialNetworks[str(text)]["Rel File"]])
            self.__objects[f'1.{len(self.__socialNetworks.keys()) + 1}'].addChild(
                self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.2"])
            addR = QtWidgets.QPushButton("Choose File")
            addR.clicked.connect(
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.2", "Social Network", str(text),
                                        "Rel File"))
            self.__windows[0].setItemWidget(self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.2"], 1, addR)
            # Adds new social network's key file
            self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.3"] = \
                QtWidgets.QTreeWidgetItem([self.__socialNetworks[str(text)]["Key File"]])
            self.__objects[f'1.{len(self.__socialNetworks.keys()) + 1}'].addChild(
                self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.3"])
            addR = QtWidgets.QPushButton("Choose File")
            addR.clicked.connect(
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.1", "Social Network", str(text),
                                        "Key File"))
            self.__windows[0].setItemWidget(self.__objects[f"1.{len(self.__socialNetworks.keys()) + 1}.3"], 1, addR)
            # Update config
            self.config.update("Social Networks", self.__socialNetworks)

    def chooseFile(self, obj, T, network, sub):
        self.__windows[2] = QtWidgets.QFileDialog()
        pathArr = self.__windows[2].getOpenFileNames(None, 'Select File', os.getenv('HOME'), "csv(*.csv)")[0]
        if pathArr is not []:
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
            self.__objects[obj].setText(0, fileName)

    def getCompleteRoadNetworks(self):
        networks = []
        for x in self.__roadNetworks:
            if self.__roadNetworks[x]["Edge File"] != "[Edge File]" and \
                    self.__roadNetworks[x]["Node File"] != "[Node File]":
                networks.append(x)
        return networks

    def getCompleteSocialNetworks(self):
        networks = []
        for x in self.__socialNetworks:
            if self.__socialNetworks[x]["Rel File"] != "[Rel File]" and \
                    self.__socialNetworks[x]["Loc File"] != "[Loc File]":
                networks.append(x)
        return networks

    def displayRoadNetwork(self, network, checked=None):
        if checked:
            self.__roadNetworkObjs[network].visualize(self.roadNetworkGraphWidget)
            self.selectedRealNetwork = self.__roadNetworkObjs[network]
        else:
            self.win.removeItem(self.roadNetworkGraphWidget)
            self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")

            self.selectedRealNetwork = None
            #self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Real Network")


    def displaySocialNetwork(self, network, checked=None):
        # TODO: When unchecked, remove points on road network also
        # TODO: add selected variable
        if checked:
            self.__socialNetworkObjs[network].visualize(self.socialNetworkGraphWidget, self.roadNetworkGraphWidget)
            self.selectedSocialNetwork = self.__socialNetworkObjs[network]
        else:
            self.win.removeItem(self.socialNetworkGraphWidget)
            self.win.removeItem(self.roadNetworkGraphWidget)
            self.selectedSocialNetwork = None
            self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
            self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")

    def getRoadNetworkInstances(self):
        for x in self.__roadNetworks:
            edges = None
            nodes = None
            if self.__roadNetworks[x]["Edge File"] != "[Edge File]":
                edges = self.__roadNetworks[x]["Edge File"]
            if self.__roadNetworks[x]["Node File"] != "[Node File]":
                nodes = self.__roadNetworks[x]["Node File"]
            self.__roadNetworkObjs[x] = RoadNetwork(x, edges, nodes)

    # noinspection SpellCheckingInspection
    def getSocialNetworkInstances(self):
        for x in self.__socialNetworks:
            rels = None
            locs = None
            if self.__socialNetworks[x]["Rel File"] != "[Rel File]":
                rels = self.__socialNetworks[x]["Rel File"]
            if self.__socialNetworks[x]["Loc File"] != "[Loc File]":
                locs = self.__socialNetworks[x]["Loc File"]
            self.__socialNetworkObjs[x] = SocialNetwork(x, rels, locs)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Closed")
        exit(0)
