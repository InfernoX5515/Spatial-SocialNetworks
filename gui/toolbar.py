from PyQt5 import QtWidgets, QtCore, QtGui
from superqt import QRangeSlider
from qtpy.QtCore import Qt

class QueryToolbar:

    def __init__(self, gui, keywordWindow, userWindow):
        self.gui = gui
        self.keywordWindow = keywordWindow
        self.userWindow = userWindow
        self.userLabel = QtWidgets.QLabel("None")
        self.keywordLabel = QtWidgets.QLabel("None")
        
    def queryUserButton(self):
        # Set up input toolbar
        self.queryUserToolbar = QtWidgets.QToolBar("queryUser")
        self.gui.addToolBar(self.queryUserToolbar)
        # Create button
        button = QtWidgets.QPushButton("Select Query User")
        button.clicked.connect(lambda: self.chooseKeywordsMenu())
        button2 = QtWidgets.QPushButton("Select Query Keyword")
        button2.clicked.connect(lambda: self.chooseQueryKeywordMenu())
        # Create label
        label = QtWidgets.QLabel("  Query User: ")
        label2 = QtWidgets.QLabel("  Query Keyword: ")
        if self.gui.queryUser is not None:
            self.userLabel = QtWidgets.QLabel(self.gui.queryUser[0].split(".0")[0])
        else:
            self.userLabel = QtWidgets.QLabel("None")
        if self.gui.queryKeyword is not None:
            self.keywordLabel = QtWidgets.QLabel(self.gui.queryKeyword)
        else:
            self.keywordLabel = QtWidgets.QLabel("None")
        # Add widgets to window
        self.queryUserToolbar.addWidget(button)
        self.queryUserToolbar.addWidget(label)
        self.queryUserToolbar.addWidget(self.userLabel)
        self.queryUserToolbar.addWidget(QtWidgets.QLabel("          "))
        self.queryUserToolbar.addWidget(button2)
        self.queryUserToolbar.addWidget(label2)
        self.queryUserToolbar.addWidget(self.keywordLabel)
    
    def chooseQueryKeywordMenu(self):
        # Window setup
        self.keywordWindow = QtWidgets.QWidget()
        self.keywordWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.keywordWindow.setWindowTitle('Choose Query Keyword')
        self.keywordWindow.resize(int(self.gui.frameGeometry().width() / 3), int(self.gui.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        self.keywordWindow.buttons = []
        # Buttons
        row = 0
        column = 0
        if self.gui.queryUser is not None:
            for keyword in self.gui.selectedSocialNetwork.getUserKeywords(self.gui.queryUser[0]):
                widget = QtWidgets.QPushButton(self.gui.selectedSocialNetwork.getKeywordByID(keyword))
                widget.clicked.connect(lambda junk, k=keyword: self.setQueryKeyword(k))
                self.keywordWindow.buttons.append(widget)
                layout.addWidget(widget, row, column)
                column += 1
                if column == 20:
                    column = 0
                    row += 1
        else:
            button = QtWidgets.QPushButton("Cancel")
            button.clicked.connect(lambda: self.keywordWindow.close())
            layout.addWidget(QtWidgets.QLabel("No Query User Selected"), 0, 0)
            layout.addWidget(button, 1, 0)
        # Show QWidget
        self.keywordWindow.setLayout(layout)
        self.keywordWindow.show()
        self.keywordWindow.move(self.gui.geometry().center() - self.keywordWindow.rect().center())
    
    def setQueryKeyword(self, keyword):
        self.gui.queryKeyword = keyword
        self.keywordLabel.setText(self.gui.selectedSocialNetwork.getKeywordByID(keyword))
        self.keywordWindow.close()

    def chooseKeywordsMenu(self):
        # Window setup
        self.keywordWindow = QtWidgets.QWidget()
        self.keywordWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.keywordWindow.setWindowTitle('Choose Keywords')
        self.keywordWindow.resize(int(self.gui.frameGeometry().width() / 3), int(self.gui.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        self.keywordWindow.checkboxes = []
        # Checkboxes
        row = 0
        column = 0
        if self.gui.selectedSocialNetwork is not None:
            for keyword in self.gui.selectedSocialNetwork.getKeywords():
                widget = QtWidgets.QCheckBox(keyword)
                self.keywordWindow.checkboxes.append(widget)
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
            button.clicked.connect(lambda: self.keywordWindow.close())
            layout.addWidget(QtWidgets.QLabel("No Social Network Selected"), 0, 0)
            layout.addWidget(button, 1, 0)
        # Show QWidget
        self.keywordWindow.setLayout(layout)
        self.keywordWindow.show()
        self.keywordWindow.move(self.gui.geometry().center() - self.keywordWindow.rect().center())

    def __showUserInfo(self, listWidget, name, username, birthdate, email, phone, keywordList, userList):
        name.setText(self.gui.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["name"])
        username.setText(self.gui.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["username"])
        birthdate.setText(self.gui.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["birthdate"])
        email.setText(self.gui.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["email"])
        phone.setText(self.gui.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["phone"])
        keywordString = ""
        for id in self.gui.selectedSocialNetwork.getUserKeywords(userList[listWidget.currentRow()]):
            keywordString += self.gui.selectedSocialNetwork.getKeywordByID(id) + ": (" + self.gui.selectedSocialNetwork.userKeywordTime(userList[listWidget.currentRow()], id)[0] + " - " + self.gui.selectedSocialNetwork.userKeywordTime(userList[listWidget.currentRow()], id)[1] + ")\n"
        keywordList.setText(keywordString)

    def showUsersWithKeywords(self):
        checkboxes = self.keywordWindow.checkboxes
        self.keywordWindow.close()
        self.userWindow = QtWidgets.QWidget()
        self.userWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.userWindow.setWindowTitle('Choose a Query User')
        self.userWindow.resize(int(self.gui.frameGeometry().width()), int(self.gui.frameGeometry().height()))
        mainLayout = QtWidgets.QVBoxLayout(self.gui)
        scroll = QtWidgets.QScrollArea(self.gui)
        self.userWindow.setLayout(mainLayout)
        mainLayout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scrollContent = QtWidgets.QWidget(scroll)
        layout = QtWidgets.QGridLayout()
        layout.setColumnStretch(2, 2)
        scrollContent.setLayout(layout)
        keywords = []
        for checkbox in checkboxes:
            if checkbox.isChecked():
                keywords.append(self.gui.selectedSocialNetwork.getIDByKeyword(checkbox.text()))
        if len(keywords) == 0:
            self.userWindow.close()
        else:
            users = self.gui.selectedSocialNetwork.getUsersWithKeywords(keywords)
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
                listWidget.addItem(self.gui.selectedSocialNetwork.getUserAttributes(user)["name"] + " (" + user.split(".0")[0] + ")")
                

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
            self.userWindow.show()
            self.userWindow.move(self.gui.geometry().center() - self.userWindow.rect().center())
        
    def setQueryUser(self, user, window=4):
        if self.gui.queryUser is not None:
            [a.clear() for a in self.gui.queryUserPlots]
            self.gui.queryUserPlots = []
        self.gui.queryUser = self.gui.selectedSocialNetwork.getUser(user)
        self.gui.plotQueryUser()
        self.userLabel.setText(user.split(".0")[0])
        # self.gui.usersCommonKeyword()
        self.userWindow.close()
        self.gui.dijkstra(self.gui.queryUser)

class Timeline:
    
    def __init__(self, gui):
        self.gui = gui
        self.toolbar = QtWidgets.QToolBar("Timeline Toolbar")
        self.timelineDateSlider = QRangeSlider(Qt.Orientation.Horizontal)
        self.timelineDateSlider.setRange(1, 365)
        self.toolbar.addWidget(self.timelineDateSlider)
        self.timelineDateSlider.valueChanged.connect(self.gui.updateTimeline)
        self.visible = False

    def show(self):
        if(self.visible):
            return
        self.gui.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)

    def hide(self):
        if(not self.visible):
            return
        self.gui.removeToolBar(self.toolbar)

    def getDates(self):
        return self.timelineDateSlider.value()
    
    def setDates(self, start, end):
        self.timelineDateSlider.setValue((start, end))

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
    