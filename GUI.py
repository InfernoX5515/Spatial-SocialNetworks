from Config import Config
from PyQt5 import QtGui
import pyqtgraph as pg
import PyQt5.QtWidgets as QtWidgets
import os
from RoadNetwork import RoadNetwork
from SocialNetwork import SocialNetwork


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
        # A dictionary of windows, each window has it's on id
        self.__windows = {}
        # TODO: Empty
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
        self.roadSummaryGraphWidget = None
        self.socialNetworkGraphWidget = None
        self.socialSummaryGraphWidget = None
        self.__menuBar()
        self.__mainWindow()

    def __mainWindow(self):
        # TODO: Make x and y pos to center of screen dynamic
        self.setGeometry(200, 200, 1000, 600)
        self.setWindowTitle("Spatial-Social Networks")
        self.setWindowIcon(QtGui.QIcon('Assets/favicon.ico'))
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.setCentralWidget(self.win)
        self.roadNetworkGraphWidget = self.win.addPlot(row=0, col=1, title="Real Network")
        self.socialNetworkGraphWidget = self.win.addPlot(row=0, col=0, title="Social Network")
        self.show()

    def __menuBar(self):
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
        viewSummaryAction = QtWidgets.QAction("Summary", self)
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
            sActions[x] = QtWidgets.QAction(x, self)
            sActions[x].setStatusTip(f"Switch to view social network {x}")
            sActions[x].triggered.connect(lambda junk, a=x: self.displaySocialNetwork(a))
            addSNMenu.addAction(sActions[x])
        # Add Real Network option
        addRNMenu = mainMenu.addMenu("Real Network")
        # Loads all road networks available
        # TODO: Look into toggle buttons for menu
        rNetworks = self.getCompleteRoadNetworks()
        rActions = {}
        for x in rNetworks:
            rActions[x] = QtWidgets.QAction(x, self)
            rActions[x].setStatusTip(f"Switch to view road network {x}")
            rActions[x].triggered.connect(lambda junk, a=x: self.displayRoadNetwork(a))
            addRNMenu.addAction(rActions[x])

    def viewSummary(self):
        # TODO: Implement summary view
        self.win.removeItem(self.roadNetworkGraphWidget)
        self.win.removeItem(self.socialNetworkGraphWidget)

    def viewFiles(self):
        self.__objects = {
            '0': QtWidgets.QTreeWidgetItem(["Road Networks"]),
            '1': QtWidgets.QTreeWidgetItem(["Social Networks"])
        }
        # TODO: Prevent drag-drop
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
            addE.clicked.connect(lambda: self.chooseFile(f"0.{len(self.__roadNetworks.keys()) + 1}.1", "Road Network", str(text),
                                        "Edge File"))
            self.__windows[0].setItemWidget(self.__objects[f"0.{len(self.__roadNetworks.keys()) + 1}.2"], 1, addE)
            # Update config
            self.config.update("Road Networks", self.__roadNetworks)

    def newSocialNetwork(self):
        # TODO: Add exceptions, add error messages
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
                lambda: self.chooseFile(f"1.{len(self.__socialNetworks.keys()) + 1}.1", "Social Network", str(text),
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

    def displayRoadNetwork(self, network):
        self.__roadNetworkObjs[network].visualize(self.roadNetworkGraphWidget)
        # self.show()

    def displaySocialNetwork(self, network):
        self.__socialNetworkObjs[network].visualize(self.socialNetworkGraphWidget)
        # self.show()

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
