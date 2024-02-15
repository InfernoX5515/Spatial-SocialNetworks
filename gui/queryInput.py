from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets

class QueryInput:
    def __init__(self, gui, keywordWindow, queryWindow):
        self.gui = gui
        self.keywordWindow = keywordWindow
        self.queryWindow = queryWindow

    def communityTime(self):
        self.__chooseCommunityKeywordsMenu(self.__communityTimeInput)

    def community(self):
        self.__chooseCommunityKeywordsMenu(self.__communityInput)

    def getCommunityKeywords(self):
        keywords = []
        for checkbox in self.keywordWindow.checkboxes:
            if checkbox.isChecked():
                keywords.append(self.gui.selectedSocialNetwork.getIDByKeyword(checkbox.text()))
        return keywords
    
    def getCommunityResponse(self):
        return self.queryWindow.kcTextBox.value(), self.queryWindow.dTextBox.text(), self.queryWindow.eTextBox.text(), self.queryWindow.kTextBox.text(), self.queryWindow.rTextBox.text(), self.queryWindow.pTextBox.text()

    def getKdResponse(self):
        return self.queryWindow.kTextBox.value(), self.queryWindow.dTextBox.text(), self.queryWindow.eTextBox.text()
    
    def kdQuery(self):
        # Window setup
        self.queryWindow = QtWidgets.QWidget()
        self.queryWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.queryWindow.setWindowTitle('Query: kd-truss')
        self.queryWindow.resize(int(self.gui.frameGeometry().width() / 3), int(self.gui.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        # Set up input toolbar
        #self.queryInput = QtWidgets.QToolBar("queryInput")
        #self.queryInput.setIconSize(QtCore.QSize(24, 24))
        #self.addToolBar(self.queryInput)
        if self.gui.queryUser is not None and self.gui.summarySelected and self.gui.selectedRoadNetwork is not None and self.gui.selectedSocialNetwork is not None:
            # Create label
            kLabel = QtWidgets.QLabel(text="community's structural cohesiveness(k): ")
            dLabel = QtWidgets.QLabel(text="maximum number of hops(d): ")
            eLabel = QtWidgets.QLabel(text="minimum degree of similarity(η): ")
            # Create button
            button = QtWidgets.QPushButton("Get Query")
            button.clicked.connect(lambda: self.gui.updateKdSummaryGraph())
            button.clicked.connect(lambda: self.queryWindow.close())
            # Create k text box
            self.queryWindow.kTextBox = QtWidgets.QSpinBox()
            self.queryWindow.kTextBox.setRange(1, 9999)
            self.queryWindow.kTextBox.setValue(3)
            self.queryWindow.kTextBox.setToolTip(
                "k is used to control the community's structural cohesiveness. Larger k means higher structural cohesiveness")
            # Create d text box
            self.queryWindow.dTextBox = QtWidgets.QLineEdit()
            self.queryWindow.dTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.dTextBox.setText("5")
            self.queryWindow.dTextBox.returnPressed.connect(button.click)
            self.queryWindow.dTextBox.setToolTip("d controls the maximum number of hops between users")
            # Create e text box
            self.queryWindow.eTextBox = QtWidgets.QLineEdit()
            self.queryWindow.eTextBox.setValidator(QtGui.QIntValidator(0, 9999))
            self.queryWindow.eTextBox.setText("0")
            self.queryWindow.eTextBox.returnPressed.connect(button.click)
            self.queryWindow.eTextBox.setToolTip("η controls the minimum degree of similarity between users")
            # Add widgets to window
            layout.addWidget(kLabel)
            layout.addWidget(self.queryWindow.kTextBox)
            layout.addWidget(dLabel)
            layout.addWidget(self.queryWindow.dTextBox)
            layout.addWidget(eLabel)
            layout.addWidget(self.queryWindow.eTextBox)
            layout.addWidget(button)
        else:
            if self.gui.selectedSocialNetwork is None:
                noSocialLabel = QtWidgets.QLabel(text="No Social Network is selected.")
                # Add widgets to window
                layout.addWidget(noSocialLabel)
            if self.gui.selectedRoadNetwork is None:
                noRoadLabel = QtWidgets.QLabel(text="No Road Network is selected.")
                # Add widgets to window
                layout.addWidget(noRoadLabel)
            if self.gui.queryUser is None:
                noUserLabel = QtWidgets.QLabel(text="No Query User is selected.")
                # Add widgets to window
                layout.addWidget(noUserLabel)
            if not self.gui.summarySelected:
                noSummaryLabel = QtWidgets.QLabel(text="Summary View is not selected.")
                # Add widgets to window
                layout.addWidget(noSummaryLabel)


        # Show QWidget
        self.queryWindow.setLayout(layout)
        self.queryWindow.show()
        self.queryWindow.move(self.gui.geometry().center() - self.queryWindow.rect().center())

    def __chooseCommunityKeywordsMenu(self, next=lambda: None):
        # Window setup
        self.keywordWindow = QtWidgets.QWidget()
        self.keywordWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.keywordWindow.setWindowTitle('Choose Keywords')
        self.keywordWindow.resize(int(self.gui.frameGeometry().width() / 3), int(self.gui.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        if self.gui.queryUser is not None and self.gui.summarySelected and self.gui.selectedRoadNetwork is not None and self.gui.selectedSocialNetwork is not None:
            self.keywordWindow.checkboxes = []
            # Checkboxes
            row = 0
            column = 0
            if self.gui.selectedSocialNetwork is not None:
                for keyword in self.gui.selectedSocialNetwork.getKeywords():
                    widget = QtWidgets.QCheckBox(keyword)
                    widget.checkState = True
                    self.keywordWindow.checkboxes.append(widget)
                    layout.addWidget(widget, row, column)
                    column += 1
                    if column == 10:
                        column = 0
                        row += 1
                button = QtWidgets.QPushButton("Ok")
                button.clicked.connect(next)
                allButton = QtWidgets.QPushButton("Select All")
                allButton.clicked.connect(lambda: self.chooseCommunityKeywordsMenuSelectAll())
                noneButton = QtWidgets.QPushButton("Select None")
                noneButton.clicked.connect(lambda: self.chooseCommunityKeywordsMenuDeselectAll())
                layout.addWidget(allButton, row + 2, 7)
                layout.addWidget(noneButton, row + 2, 8)
                layout.addWidget(button, row + 3, 8)
            else:
                button = QtWidgets.QPushButton("Cancel")
                button.clicked.connect(lambda: self.keywordWindow.close())
                layout.addWidget(QtWidgets.QLabel("No Social Network Selected"), 0, 0)
                layout.addWidget(button, 1, 0)
        else:
            if self.gui.selectedSocialNetwork is None:
                noSocialLabel = QtWidgets.QLabel(text="No Social Network is selected.")
                # Add widgets to window
                layout.addWidget(noSocialLabel)
            if self.gui.selectedRoadNetwork is None:
                noRoadLabel = QtWidgets.QLabel(text="No Road Network is selected.")
                # Add widgets to window
                layout.addWidget(noRoadLabel)
            if self.gui.queryUser is None:
                noUserLabel = QtWidgets.QLabel(text="No Query User is selected.")
                # Add widgets to window
                layout.addWidget(noUserLabel)
            if not self.gui.summarySelected:
                noSummaryLabel = QtWidgets.QLabel(text="Summary View is not selected.")
                # Add widgets to window
                layout.addWidget(noSummaryLabel)
        # Show QWidget
        self.keywordWindow.setLayout(layout)
        self.keywordWindow.show()
        self.keywordWindow.move(self.gui.geometry().center() - self.keywordWindow.rect().center())


    def chooseCommunityKeywordsMenuSelectAll(self):
        for checkbox in self.keywordWindow.checkboxes:
            checkbox.setCheckState(QtCore.Qt.Checked)
    
    def chooseCommunityKeywordsMenuDeselectAll(self):
        for checkbox in self.keywordWindow.checkboxes:
            checkbox.setCheckState(QtCore.Qt.Unchecked)

    
    def __communityInput(self):
        self.keywordWindow.close()
        # Window setup
        self.queryWindow = QtWidgets.QWidget()
        self.queryWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.queryWindow.setWindowTitle('Query: Community Search')
        self.queryWindow.resize(int(self.gui.frameGeometry().width() / 3), int(self.gui.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        # Set up input toolbar
        #self.queryInput = QtWidgets.QToolBar("queryInput")
        #self.queryInput.setIconSize(QtCore.QSize(24, 24))
        #self.addToolBar(self.queryInput)
        if self.gui.queryUser is not None and self.gui.summarySelected and self.gui.selectedRoadNetwork is not None and self.gui.selectedSocialNetwork is not None:
            # Create label
            kcLabel = QtWidgets.QLabel(text="community's structural cohesiveness(k): ")
            dLabel = QtWidgets.QLabel(text="maximum number of hops(d): ")
            eLabel = QtWidgets.QLabel(text="minimum similarity threshold (η): ")
            keyWeightLabel = QtWidgets.QLabel(text="weight of keywords (g): ")
            relWeightLabel = QtWidgets.QLabel(text="weight of relationships (h): ")
            poiWeightLabel = QtWidgets.QLabel(text="weight of POIs (m): ")
            # Create button
            button = QtWidgets.QPushButton("Get Query")
            button.clicked.connect(lambda: self.gui.updateCommunitySummaryGraph())
            button.clicked.connect(lambda: self.queryWindow.close())
            # Create k text box
            self.queryWindow.kcTextBox = QtWidgets.QSpinBox()
            self.queryWindow.kcTextBox.setRange(1, 9999)
            self.queryWindow.kcTextBox.setValue(3)
            self.queryWindow.kcTextBox.setToolTip(
                "k is used to control the community's structural cohesiveness. Larger k means higher structural cohesiveness")
            # Create d text box
            self.queryWindow.dTextBox = QtWidgets.QLineEdit()
            self.queryWindow.dTextBox.setValidator(QtGui.QIntValidator(0, 9999))
            self.queryWindow.dTextBox.setText("5")
            self.queryWindow.dTextBox.returnPressed.connect(button.click)
            self.queryWindow.dTextBox.setToolTip("d controls the maximum number of hops between users")
            # Create e text box
            self.queryWindow.eTextBox = QtWidgets.QLineEdit()
            self.queryWindow.eTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.eTextBox.setText("0")
            self.queryWindow.eTextBox.returnPressed.connect(button.click)
            self.queryWindow.eTextBox.setToolTip("η controls the minimum similarity threshold between users")
            # Create k text box
            self.queryWindow.kTextBox = QtWidgets.QLineEdit()
            self.queryWindow.kTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.kTextBox.setText("0.4")
            self.queryWindow.kTextBox.returnPressed.connect(button.click)
            self.queryWindow.kTextBox.setToolTip("g controls the weight for keyword for degree of similarity")
            # Create r text box
            self.queryWindow.rTextBox = QtWidgets.QLineEdit()
            self.queryWindow.rTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.rTextBox.setText("0.4")
            self.queryWindow.rTextBox.returnPressed.connect(button.click)
            self.queryWindow.rTextBox.setToolTip("h controls the weight for relationships for degree of similarity")
            # Create p text box
            self.queryWindow.pTextBox = QtWidgets.QLineEdit()
            self.queryWindow.pTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.pTextBox.setText("0.2")
            self.queryWindow.pTextBox.returnPressed.connect(button.click)
            self.queryWindow.pTextBox.setToolTip("m controls the weight for POIs for degree of similarity")
            # Add widgets to window
            layout.addWidget(kcLabel)
            layout.addWidget(self.queryWindow.kcTextBox)
            layout.addWidget(dLabel)
            layout.addWidget(self.queryWindow.dTextBox)
            layout.addWidget(eLabel)
            layout.addWidget(self.queryWindow.eTextBox)
            layout.addWidget(keyWeightLabel)
            layout.addWidget(self.queryWindow.kTextBox)
            layout.addWidget(relWeightLabel)
            layout.addWidget(self.queryWindow.rTextBox)
            layout.addWidget(poiWeightLabel)
            layout.addWidget(self.queryWindow.pTextBox)
            layout.addWidget(button)
        else:
            if self.gui.selectedSocialNetwork is None:
                noSocialLabel = QtWidgets.QLabel(text="No Social Network is selected.")
                # Add widgets to window
                layout.addWidget(noSocialLabel)
            if self.gui.selectedRoadNetwork is None:
                noRoadLabel = QtWidgets.QLabel(text="No Road Network is selected.")
                # Add widgets to window
                layout.addWidget(noRoadLabel)
            if self.gui.queryUser is None:
                noUserLabel = QtWidgets.QLabel(text="No Query User is selected.")
                # Add widgets to window
                layout.addWidget(noUserLabel)
            if not self.gui.summarySelected:
                noSummaryLabel = QtWidgets.QLabel(text="Summary View is not selected.")
                # Add widgets to window
                layout.addWidget(noSummaryLabel)


        # Show QWidget
        self.queryWindow.setLayout(layout)
        self.queryWindow.show()
        self.queryWindow.move(self.gui.geometry().center() - self.queryWindow.rect().center())
    
    def __communityTimeInput(self):
        #checkboxes = self.keywordWindow.checkboxes
        self.keywordWindow.close()
        # Window setup
        self.queryWindow = QtWidgets.QWidget()
        self.queryWindow.setWindowModality(QtCore.Qt.ApplicationModal)
        self.queryWindow.setWindowTitle('Query: Community Search w/ Time')
        self.queryWindow.resize(int(self.gui.frameGeometry().width() / 3), int(self.gui.frameGeometry().height() / 3))
        layout = QtWidgets.QGridLayout()
        # Set up input toolbar
        #self.queryInput = QtWidgets.QToolBar("queryInput")
        #self.queryInput.setIconSize(QtCore.QSize(24, 24))
        #self.addToolBar(self.queryInput)
        if self.gui.queryUser is not None and self.gui.summarySelected and self.gui.selectedRoadNetwork is not None and self.gui.selectedSocialNetwork is not None:
            # Create label
            kcLabel = QtWidgets.QLabel(text="community's structural cohesiveness(k): ")
            dLabel = QtWidgets.QLabel(text="maximum number of hops(d): ")
            eLabel = QtWidgets.QLabel(text="minimum similarity threshold (η): ")
            tLabel = QtWidgets.QLabel(text="keyword time overlap % (t): ")
            keyWeightLabel = QtWidgets.QLabel(text="weight of keywords (g): ")
            relWeightLabel = QtWidgets.QLabel(text="weight of relationships (h): ")
            poiWeightLabel = QtWidgets.QLabel(text="weight of POIs (m): ")
            # Create button
            button = QtWidgets.QPushButton("Get Query")
            button.clicked.connect(lambda: self.gui.updateCommunitySummaryGraph())
            button.clicked.connect(lambda: self.queryWindow.close())
            # Create k text box
            self.queryWindow.kcTextBox = QtWidgets.QSpinBox()
            self.queryWindow.kcTextBox.setRange(1, 9999)
            self.queryWindow.kcTextBox.setValue(3)
            self.queryWindow.kcTextBox.setToolTip(
                "k is used to control the community's structural cohesiveness. Larger k means higher structural cohesiveness")
            # Create d text box
            self.queryWindow.dTextBox = QtWidgets.QLineEdit()
            self.queryWindow.dTextBox.setValidator(QtGui.QIntValidator(0, 9999))
            self.queryWindow.dTextBox.setText("5")
            self.queryWindow.dTextBox.returnPressed.connect(button.click)
            self.queryWindow.dTextBox.setToolTip("d controls the maximum number of hops between users")
            # Create e text box
            self.queryWindow.eTextBox = QtWidgets.QLineEdit()
            self.queryWindow.eTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.eTextBox.setText("0")
            self.queryWindow.eTextBox.returnPressed.connect(button.click)
            self.queryWindow.eTextBox.setToolTip("η controls the minimum similarity threshold between users")
            # Create k text box
            self.queryWindow.kTextBox = QtWidgets.QLineEdit()
            self.queryWindow.kTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.kTextBox.setText("0.4")
            self.queryWindow.kTextBox.returnPressed.connect(button.click)
            self.queryWindow.kTextBox.setToolTip("g controls the weight for keyword for degree of similarity")
            # Create r text box
            self.queryWindow.rTextBox = QtWidgets.QLineEdit()
            self.queryWindow.rTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.rTextBox.setText("0.4")
            self.queryWindow.rTextBox.returnPressed.connect(button.click)
            self.queryWindow.rTextBox.setToolTip("h controls the weight for relationships for degree of similarity")
            # Create p text box
            self.queryWindow.pTextBox = QtWidgets.QLineEdit()
            self.queryWindow.pTextBox.setValidator(QtGui.QDoubleValidator(0.0, 9999.0, 4))
            self.queryWindow.pTextBox.setText("0.2")
            self.queryWindow.pTextBox.returnPressed.connect(button.click)
            self.queryWindow.pTextBox.setToolTip("m controls the weight for POIs for degree of similarity")
            # Create t text box
            self.queryWindow.tTextBox = QtWidgets.QLineEdit()
            self.queryWindow.tTextBox.setValidator(QtGui.QDoubleValidator(0.0, 1.0, 4))
            self.queryWindow.tTextBox.setText("0.5")
            self.queryWindow.tTextBox.returnPressed.connect(button.click)
            self.queryWindow.tTextBox.setToolTip("t controls the keyword time overlap")

            # Add widgets to window
            layout.addWidget(kcLabel)
            layout.addWidget(self.queryWindow.kcTextBox)
            layout.addWidget(dLabel)
            layout.addWidget(self.queryWindow.dTextBox)
            layout.addWidget(eLabel)
            layout.addWidget(self.queryWindow.eTextBox)
            layout.addWidget(tLabel)
            layout.addWidget(self.queryWindow.tTextBox)
            layout.addWidget(keyWeightLabel)
            layout.addWidget(self.queryWindow.kTextBox)
            layout.addWidget(relWeightLabel)
            layout.addWidget(self.queryWindow.rTextBox)
            layout.addWidget(poiWeightLabel)
            layout.addWidget(self.queryWindow.pTextBox)
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
        self.queryWindow.setLayout(layout)
        self.queryWindow.show()
        self.queryWindow.move(self.gui.geometry().center() - self.queryWindow.rect().center())