from PyQt5 import QtWidgets, QtCore, QtGui
# from GUI import Gui as g

#class Mixin:
class Toolbar:

    # _instance = None

    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super(Toolbar, cls).__new__(cls)
    #         return cls._instance
    #     else:
    #         return cls._instance

    def __init__(self, gui):
        self.gui = gui

    def zoomOutTool(self):
        xRanges = self.gui.roadGraphWidget.getAxis('bottom').range
        yRanges = self.gui.roadGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.gui.roadGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] + xScale)
        self.gui.roadGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] + yScale)

    def zoomInTool(self):
        xRanges = self.gui.roadGraphWidget.getAxis('bottom').range
        yRanges = self.gui.roadGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.gui.roadGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] - xScale)
        self.gui.roadGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] - yScale)

    def jogLeftTool(self):
        xRanges = self.gui.roadGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.gui.roadGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] - xScale, padding=0)

    def jogRightTool(self):
        xRanges = self.gui.roadGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.gui.roadGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] + xScale, padding=0)

    def jogUpTool(self):
        yRanges = self.gui.roadGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.gui.roadGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] + yScale, padding=0)

    def jogDownTool(self):
        yRanges = self.gui.roadGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.gui.roadGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] - yScale, padding=0)



    def zoomOutToolSocial(self):
        xRanges = self.gui.socialGraphWidget.getAxis('bottom').range
        yRanges = self.gui.socialGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.gui.socialGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] + xScale)
        self.gui.socialGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] + yScale)

    def zoomInToolSocial(self):
        xRanges = self.gui.socialGraphWidget.getAxis('bottom').range
        yRanges = self.gui.socialGraphWidget.getAxis('left').range
        xScale, yScale = self.getZoomScale(xRanges, yRanges)
        self.gui.socialGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] - xScale)
        self.gui.socialGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] - yScale)

    def jogLeftToolSocial(self):
        xRanges = self.gui.socialGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.gui.socialGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] - xScale, padding=0)

    def jogRightToolSocial(self):
        xRanges = self.gui.socialGraphWidget.getAxis('bottom').range
        xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2
        self.gui.socialGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] + xScale, padding=0)

    def jogUpToolSocial(self):
        yRanges = self.gui.socialGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.gui.socialGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] + yScale, padding=0)

    def jogDownToolSocial(self):
        yRanges = self.gui.socialGraphWidget.getAxis('left').range
        yScale = (abs(yRanges[1] - yRanges[0]) * .25) / 2
        self.gui.socialGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] - yScale, padding=0)

    def zoomInToolInteractive(self):
        self.gui.socialNetWidget.page().runJavaScript(r"network.moveTo({scale: network.getScale()+0.2});")

    def zoomOutToolInteractive(self):
        self.gui.socialNetWidget.page().runJavaScript(r"network.moveTo({scale: network.getScale()-0.2});")

    def jogUpToolInteractive(self):
        self.gui.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x'], y:t['y']-20}});")

    def jogDownToolInteractive(self):
        self.gui.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x'], y:t['y']+20}});")

    def jogRightToolInteractive(self):
        self.gui.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x']+20, y:t['y']}});")

    def jogLeftToolInteractive(self):
        self.gui.socialNetWidget.page().runJavaScript(r"var t = network.getViewPosition(); network.moveTo({position: {x:t['x']-20, y:t['y']}});")

    @staticmethod
    def getZoomScale(xRanges, yRanges):
        # Percent to zoom
        percent = .25
        xLen = abs(xRanges[1] - xRanges[0])
        yLen = abs(yRanges[1] - yRanges[0])
        xScale = (xLen * percent) / 2
        yScale = (yLen * percent) / 2
        return xScale, yScale

    
    # Creates the navigation toolbar
    def navToolbar(self):
        # Create toolbar for road graph
        toolbar = QtWidgets.QToolBar("Navigation Toolbar")
        toolbar.setIconSize(QtCore.QSize(24, 24))
        #self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)
        # Zoom in
        zoom_in = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self.gui)
        zoom_in.triggered.connect(self.zoomInTool)
        toolbar.addAction(zoom_in)
        # Zoom out
        zoom_out = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self.gui)
        zoom_out.triggered.connect(self.zoomOutTool)
        toolbar.addAction(zoom_out)
        # Jog left
        jogLeft = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self.gui)
        jogLeft.triggered.connect(self.jogLeftTool)
        toolbar.addAction(jogLeft)
        # Jog right
        jogRight = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self.gui)
        jogRight.triggered.connect(self.jogRightTool)
        toolbar.addAction(jogRight)
        # Jog up
        jogUp = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self.gui)
        jogUp.triggered.connect(self.jogUpTool)
        toolbar.addAction(jogUp)
        # Jog down
        jogDown = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-down-solid.svg'), "Jog Down", self.gui)
        jogDown.triggered.connect(self.jogDownTool)
        toolbar.addAction(jogDown)
        if self.gui.summarySelected:
            self.gui.sumLayout.addWidget(toolbar, 1, 1)
            # Create a second toolbar for the social graph
            socialToolbar = QtWidgets.QToolBar("Navigation Toolbar")
            socialToolbar.setIconSize(QtCore.QSize(24, 24))
            #self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)
            # Zoom in
            zoom_in_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self.gui)
            zoom_in_social.triggered.connect(self.zoomInToolInteractive)
            socialToolbar.addAction(zoom_in_social)
            # Zoom out
            zoom_out_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self.gui)
            zoom_out_social.triggered.connect(self.zoomOutToolInteractive)
            socialToolbar.addAction(zoom_out_social)
            # Jog left
            jogLeft_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self.gui)
            jogLeft_social.triggered.connect(self.jogLeftToolInteractive)
            socialToolbar.addAction(jogLeft_social)
            # Jog right
            jogRight_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self.gui)
            jogRight_social.triggered.connect(self.jogRightToolInteractive)
            socialToolbar.addAction(jogRight_social)
            # Jog up
            jogUp_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self.gui)
            jogUp_social.triggered.connect(self.jogUpToolInteractive)
            socialToolbar.addAction(jogUp_social)
            # Jog down
            jogDown_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-down-solid.svg'), "Jog Down", self.gui)
            jogDown_social.triggered.connect(self.jogDownToolInteractive)
            socialToolbar.addAction(jogDown_social)
            self.gui.sumLayout.addWidget(socialToolbar, 1, 0)
        else:
            # Add the toolbar to the road graph
            self.gui.layout.addWidget(toolbar, 1, 1)
            # Create a second toolbar for the social graph
            socialToolbar = QtWidgets.QToolBar("Navigation Toolbar")
            socialToolbar.setIconSize(QtCore.QSize(24, 24))
            #self.addToolBar(QtCore.Qt.BottomToolBarArea, toolbar)
            # Zoom in
            zoom_in_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-plus-solid.svg'), "Zoom In", self.gui)
            zoom_in_social.triggered.connect(self.zoomInToolSocial)
            socialToolbar.addAction(zoom_in_social)
            # Zoom out
            zoom_out_social = QtWidgets.QAction(QtGui.QIcon('Assets/magnifying-glass-minus-solid.svg'), "Zoom Out", self.gui)
            zoom_out_social.triggered.connect(self.zoomOutToolSocial)
            socialToolbar.addAction(zoom_out_social)
            # Jog left
            jogLeft_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-left-solid.svg'), "Jog Left", self.gui)
            jogLeft_social.triggered.connect(self.jogLeftToolSocial)
            socialToolbar.addAction(jogLeft_social)
            # Jog right
            jogRight_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-right-solid.svg'), "Jog Right", self.gui)
            jogRight_social.triggered.connect(self.jogRightToolSocial)
            socialToolbar.addAction(jogRight_social)
            # Jog up
            jogUp_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-up-solid.svg'), "Jog Up", self.gui)
            jogUp_social.triggered.connect(self.jogUpToolSocial)
            socialToolbar.addAction(jogUp_social)
            # Jog down
            jogDown_social = QtWidgets.QAction(QtGui.QIcon('Assets/arrow-down-solid.svg'), "Jog Down", self.gui)
            jogDown_social.triggered.connect(self.jogDownToolSocial)
            socialToolbar.addAction(jogDown_social)
            self.gui.layout.addWidget(socialToolbar, 1, 0)
    
    # Creates the cluster toolbar for input
    def clusterInput(self):
        # Set up input toolbar
        self.clusterInput = QtWidgets.QToolBar("clusterInput")
        self.clusterInput.setIconSize(QtCore.QSize(24, 24))
        #self.keywordInput = QtWidgets.QToolBar("keyowrdInput")
        #self.keywordInput.setIconSize(QtCore.QSize(24, 24))
        #self.distanceInput = QtWidgets.QToolBar("distanceInput")
        #self.distanceInput.setIconSize(QtCore.QSize(24, 24))
        self.gui.addToolBar(self.clusterInput)
        # Create labels
        nLabel = QtWidgets.QLabel(text="n-clusters: ")
        #kLabel = QtWidgets.QLabel(text="keywords: ")
        #dLabel = QtWidgets.QLabel(text="distance: ")
        # Create buttons
        button = QtWidgets.QPushButton("Ok")
        button.clicked.connect(lambda: self.gui.updateSummaryGraph())
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
    