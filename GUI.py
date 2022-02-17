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
    def __init__(self):
        super(Gui, self).__init__()
        self.config = Config()
        # Enable antialiasing for prettier plots
        pg.setConfigOptions(antialias=True)
        # Sets styling
        pg.setConfigOption('background', 'white')
        # A dictionary of windows, each window has it's on id
        self.__windows = {}
        # Stores all road network info
        self.__roadNetworks = self.config.settings["Road Networks"]
        # Stores road network objects
        self.__roadNetworkObjs = {}
        # Gets instances of finished road networks
        self.getRoadNetworkInstances()
        # Stores all social network info
        self.__socialNetworks = self.config.settings["Social Networks"]
        # Stores social network objects
        self.__socialNetworkObjs = {}
        # Gets instances of finished social networks
        self.getSocialNetworkInstances()
        # Stores file hierarchy data
        self.__objects = {}
        # Stores widget instances
        self.roadNetworkGraphWidget = None
        self.socialNetworkGraphWidget = None
        self.roadSummaryGraphWidget = None
        self.socialSummaryGraphWidget = None
        # Stores selected network instances
        self.selectedRoadNetwork = None
        self.selectedSocialNetwork = None
        # Initializes menus
        self.__menuBar()
        self.__toolbar()
        self.__mainWindow()

    def __mainWindow(self):
        screensize = self.screen().availableSize().width(), self.screen().availableSize().height()
        self.setGeometry(int((screensize[0] / 2) - 500), int((screensize[1] / 2) - 300), 1000, 600)
        self.setWindowTitle("Spatial-Social Networks")
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.win)
        # Create and set up road network graph widget
        self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
        # Create and set up the social network graph widget
        self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
        # Links the x and y axis on both graphs
        self.socialNetworkGraphWidget.setXLink(self.roadNetworkGraphWidget)
        self.socialNetworkGraphWidget.setYLink(self.roadNetworkGraphWidget)
        # Draw crosshairs on graph
        self.socialNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
        self.socialNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
        self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.vCrossLine, ignoreBounds=True)
        self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.hCrossLine, ignoreBounds=True)
        self.roadNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
        self.roadNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
        self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.vCrossLine, ignoreBounds=True)
        self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.hCrossLine, ignoreBounds=True)
        # Adds event listener
        self.roadNetworkGraphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        # Show window
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
        #self.roadNetworkGraphWidget.viewRange =  [
        # [-124.8716955920008 + (-124.8716955920008 * .5), -113.81190540799919 - (-113.81190540799919 * 0.5)],
        # [32.08680962346822 + (32.08680962346822 * 0.5), 42.47730737653178 - (42.47730737653178 * .5)]]
        #self.roadNetworkGraphWidget.setXRange((
        # self.roadNetworkGraphWidget.viewRange[0][0] * 1.75) +  self.roadNetworkGraphWidget.viewRange[0][0],
        # self.roadNetworkGraphWidget.viewRange[0][1] - (self.roadNetworkGraphWidget.viewRange[0][1] * 1.75))
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

    def viewSummary(self):
        # If not viewing summary already, view it, otherwise, display main view again
        if self.roadSummaryGraphWidget is None and self.socialSummaryGraphWidget is None:
            # TODO: Add plots for social network summary
            # Clears last view
            self.win.removeItem(self.roadNetworkGraphWidget)
            self.win.removeItem(self.socialNetworkGraphWidget)
            # Displays summary plots
            self.socialSummaryGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
            self.roadSummaryGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
            # Draw crosshairs on graph
            self.socialSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
            self.socialSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
            self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.vCrossLine, ignoreBounds=True)
            self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.hCrossLine, ignoreBounds=True)
            self.roadSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
            self.roadSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
            self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.vCrossLine, ignoreBounds=True)
            self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.hCrossLine, ignoreBounds=True)
            # Adds event listener
            self.roadSummaryGraphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
            # Links the x and y axis on both graphs
            self.socialSummaryGraphWidget.setXLink(self.roadSummaryGraphWidget)
            self.socialSummaryGraphWidget.setYLink(self.roadSummaryGraphWidget)
            # If both a road network is selected, display info
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadSummaryGraphWidget)
                # TODO: Add user-defined n_cluster amount
                # If social network is selected, display clusters
                if self.selectedSocialNetwork is not None:
                    # Draws summary nodes on graph. n_clusters is th number of nodes to plot
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
                    self.roadSummaryGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=30,
                                                 symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
        else:
            self.win.removeItem(self.roadSummaryGraphWidget)
            self.win.removeItem(self.socialSummaryGraphWidget)
            self.roadSummaryGraphWidget = None
            self.socialSummaryGraphWidget = None
            self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
            self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
            # Re-visualize selected networks
            if self.selectedRoadNetwork is not None:
                self.selectedRoadNetwork.visualize(self.roadNetworkGraphWidget)
            if self.selectedSocialNetwork is not None:
                self.selectedSocialNetwork.visualize(self.socialNetworkGraphWidget, self.roadNetworkGraphWidget)

    def viewFiles(self):
        self.__objects = {
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
            self.menuBar().clear()
            self.__menuBar()

    def chooseFile(self, obj, T, network, sub):
        self.__windows[2] = QtWidgets.QFileDialog()
        pathArr = self.__windows[2].getOpenFileNames(None, 'Select File', os.getenv('HOME'), "csv(*.csv)")[0]
        if len(pathArr) is not 0:
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
        self.menuBar().clear()
        self.__menuBar()

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
        if self.roadSummaryGraphWidget is None:
            if checked:
                self.win.removeItem(self.socialNetworkGraphWidget)
                self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.win.removeItem(self.roadNetworkGraphWidget)
                self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # If there is a social network selected, remove and re-add to make sure nodes stay above the plot
                if self.selectedSocialNetwork is not None:
                    # Visualize
                    self.selectedSocialNetwork.visualize(self.socialNetworkGraphWidget, self.roadNetworkGraphWidget)
                # Visualizes the graph that is being selected
                self.__roadNetworkObjs[network].visualize(self.roadNetworkGraphWidget)
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
            else:
                # Removes the widget and re-adds it to be blank
                self.win.removeItem(self.roadNetworkGraphWidget)
                self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                self.selectedRoadNetwork = None
                self.win.removeItem(self.socialNetworkGraphWidget)
                self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                # Removes the social network and re-adds it to keep the graph there
                if self.selectedSocialNetwork is not None:
                    self.selectedSocialNetwork.visualize(self.socialNetworkGraphWidget, self.roadNetworkGraphWidget)
            # Draw crosshairs on graph
            self.roadNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
            self.roadNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
            self.socialNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
            self.socialNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
            self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.vCrossLine, ignoreBounds=True)
            self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.hCrossLine, ignoreBounds=True)
            self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.vCrossLine, ignoreBounds=True)
            self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.hCrossLine, ignoreBounds=True)
            # Links the x and y axis on both graphs
            self.socialNetworkGraphWidget.setXLink(self.roadNetworkGraphWidget)
            self.socialNetworkGraphWidget.setYLink(self.roadNetworkGraphWidget)
        else:
            if checked:
                self.win.removeItem(self.socialSummaryGraphWidget)
                self.socialSummaryGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                self.win.removeItem(self.roadSummaryGraphWidget)
                self.roadSummaryGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                self.selectedRoadNetwork = self.__roadNetworkObjs[network]
                self.selectedRoadNetwork.visualize(self.roadSummaryGraphWidget)
                # If there is a social network selected, remove and re-add to make sure nodes stay above the plot
                if self.selectedSocialNetwork is not None:
                    # Draws summary nodes on graph. n_clusters is th number of nodes to plot
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
                    self.roadSummaryGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=30,
                                                     symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                self.socialSummaryGraphWidget.setXLink(self.roadSummaryGraphWidget)
                self.socialSummaryGraphWidget.setYLink(self.roadSummaryGraphWidget)
                # Draw crosshairs on graph
                self.socialSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.socialSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.vCrossLine, ignoreBounds=True)
                self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.hCrossLine, ignoreBounds=True)
                self.roadSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.roadSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.vCrossLine, ignoreBounds=True)
                self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.hCrossLine, ignoreBounds=True)
            else:
                # Removes the widget and re-adds it to be blank
                self.win.removeItem(self.roadSummaryGraphWidget)
                self.roadSummaryGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                self.selectedRoadNetwork = None
                self.win.removeItem(self.socialSummaryGraphWidget)
                self.socialSummaryGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                # Removes the social network and re-adds it to keep the graph there
                if self.selectedSocialNetwork is not None:
                    self.selectedSocialNetwork.visualize(self.socialSummaryGraphWidget, self.roadSummaryGraphWidget)
            # Draw crosshairs on graph
            self.roadSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
            self.roadSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
            self.socialSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
            self.socialSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
            self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.vCrossLine, ignoreBounds=True)
            self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.hCrossLine, ignoreBounds=True)
            self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.vCrossLine, ignoreBounds=True)
            self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.hCrossLine, ignoreBounds=True)
            # Links the x and y axis on both graphs
            self.socialSummaryGraphWidget.setXLink(self.roadSummaryGraphWidget)
            self.socialSummaryGraphWidget.setYLink(self.roadSummaryGraphWidget)

    def displaySocialNetwork(self, network, checked=None):
        # TODO: Fix issue where unchecking road network in summary switches back to normal view
        if self.socialSummaryGraphWidget is None:
            if checked:
                # Visualizes social network
                self.__socialNetworkObjs[network].visualize(self.socialNetworkGraphWidget, self.roadNetworkGraphWidget)
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
            else:
                # Removes both graphs to clear them then re-adds them
                self.win.removeItem(self.socialNetworkGraphWidget)
                self.win.removeItem(self.roadNetworkGraphWidget)
                self.selectedSocialNetwork = None
                self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # Re-visualizes the road network if it is selected
                if self.selectedRoadNetwork:
                    self.selectedRoadNetwork.visualize(self.roadNetworkGraphWidget)
                # Draw crosshairs on graph
                self.roadNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.roadNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.socialNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.socialNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.vCrossLine, ignoreBounds=True)
                self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.hCrossLine, ignoreBounds=True)
                self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.vCrossLine, ignoreBounds=True)
                self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.hCrossLine, ignoreBounds=True)
        else:
            if checked:
                self.selectedSocialNetwork = self.__socialNetworkObjs[network]
                self.win.removeItem(self.socialSummaryGraphWidget)
                self.socialSummaryGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network Summary")
                self.win.removeItem(self.roadSummaryGraphWidget)
                self.roadSummaryGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network Summary")
                if self.selectedRoadNetwork is not None:
                    self.selectedRoadNetwork.visualize(self.roadSummaryGraphWidget)
                # Draws summary nodes on graph. n_clusters is th number of nodes to plot
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
                self.roadSummaryGraphWidget.plot(centers[:, 0], centers[:, 1], pen=None, symbol='o', symbolSize=30,
                                                 symbolPen=(255, 0, 0), symbolBrush=(255, 0, 0, 125))
                self.socialSummaryGraphWidget.setXLink(self.roadSummaryGraphWidget)
                self.socialSummaryGraphWidget.setYLink(self.roadSummaryGraphWidget)
                # Draw crosshairs on graph
                self.socialSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.socialSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.vCrossLine, ignoreBounds=True)
                self.socialSummaryGraphWidget.addItem(self.socialSummaryGraphWidget.hCrossLine, ignoreBounds=True)
                self.roadSummaryGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.roadSummaryGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.vCrossLine, ignoreBounds=True)
                self.roadSummaryGraphWidget.addItem(self.roadSummaryGraphWidget.hCrossLine, ignoreBounds=True)
            else:
                # TODO: Implement
                print("")
                # Removes both graphs to clear them then re-adds them
                '''self.win.removeItem(self.socialNetworkGraphWidget)
                self.win.removeItem(self.roadNetworkGraphWidget)
                self.selectedSocialNetwork = None
                self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
                self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Road Network")
                # Re-visualizes the road network if it is selected
                if self.selectedRoadNetwork:
                    self.selectedRoadNetwork.visualize(self.roadNetworkGraphWidget)
                # Draw crosshairs on graph
                self.roadNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.roadNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.socialNetworkGraphWidget.vCrossLine = pg.InfiniteLine(angle=90, movable=False)
                self.socialNetworkGraphWidget.hCrossLine = pg.InfiniteLine(angle=0, movable=False)
                self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.vCrossLine, ignoreBounds=True)
                self.socialNetworkGraphWidget.addItem(self.socialNetworkGraphWidget.hCrossLine, ignoreBounds=True)
                self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.vCrossLine, ignoreBounds=True)
                self.roadNetworkGraphWidget.addItem(self.roadNetworkGraphWidget.hCrossLine, ignoreBounds=True)'''

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

    def mouseMoved(self, evt):
        mousePoint = None
        # Sets the mousePoint to whichever graph the pointer is over
        if self.roadNetworkGraphWidget.sceneBoundingRect().contains(evt.x(), evt.y()):
            mousePoint = self.roadNetworkGraphWidget.vb.mapSceneToView(evt)
        else:
            if self.roadSummaryGraphWidget is not None:
                if self.socialSummaryGraphWidget.sceneBoundingRect().contains(evt.x(), evt.y()):
                    mousePoint = self.socialSummaryGraphWidget.vb.mapSceneToView(evt)
                else:
                    mousePoint = self.roadSummaryGraphWidget.vb.mapSceneToView(evt)
            else:
                mousePoint = self.socialNetworkGraphWidget.vb.mapSceneToView(evt)
        # TODO: Implement x, y coords to show
        # Changes text for position
        '''index = int(mousePoint.x())
        if index > 0 and index < len(data1):
           label.setText(
                "<span style='font-size: 12pt'>x=%0.1f,   <span style='color: red'>y1=%0.1f</span>,   <span style='color: green'>y2=%0.1f</span>" % (
                mousePoint.x(), data1[index], data2[index]))'''
        if mousePoint is not None:
            if self.roadSummaryGraphWidget is None:
                # Moves the road network crosshair
                self.roadNetworkGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.roadNetworkGraphWidget.hCrossLine.setPos(mousePoint.y())
                # Moves the social network crosshair
                self.socialNetworkGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.socialNetworkGraphWidget.hCrossLine.setPos(mousePoint.y())
            else:
                # Moves the road network crosshair
                self.roadSummaryGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.roadSummaryGraphWidget.hCrossLine.setPos(mousePoint.y())
                # Moves the social network crosshair
                self.socialSummaryGraphWidget.vCrossLine.setPos(mousePoint.x())
                self.socialSummaryGraphWidget.hCrossLine.setPos(mousePoint.y())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        print("Closed")
        exit(0)
