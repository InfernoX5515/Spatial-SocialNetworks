from PyQt5 import QtWidgets, QtCore, QtGui

class UserUI:

    def __init__(self, gui, window):
        self.gui = gui
        self.window = window
        self.selectedSocialNetwork = self.gui.selectedSocialNetwork

    def __showUserInfo(self, listWidget, name, username, birthdate, email, phone, keywordList, userList):
        name.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["name"])
        username.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["username"])
        birthdate.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["birthdate"])
        email.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["email"])
        phone.setText(self.selectedSocialNetwork.getUserAttributes(userList[listWidget.currentRow()])["phone"])
        keywordString = ""
        for id in self.selectedSocialNetwork.getUserKeywords(userList[listWidget.currentRow()]):
            keywordString += self.selectedSocialNetwork.getKeywordByID(id) + ": (" + self.gui.selectedSocialNetwork.userKeywordTime(userList[listWidget.currentRow()], id)[0] + " - " + self.gui.selectedSocialNetwork.userKeywordTime(userList[listWidget.currentRow()], id)[1] + ")\n"
        keywordList.setText(keywordString)

    def showClusterUsers(self, users):
        self.window = QtWidgets.QWidget()
        self.window.setWindowModality(QtCore.Qt.ApplicationModal)
        self.window.setWindowTitle('Cluster Users')
        self.window.resize(int(self.gui.frameGeometry().width()), int(self.gui.frameGeometry().height()))

        mainLayout = QtWidgets.QVBoxLayout(self.gui)
        scroll = QtWidgets.QScrollArea(self.gui)
        self.window.setLayout(mainLayout)
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
        setQueryUsr.clicked.connect(lambda: self.gui.setQueryUser(userList[listWidget.currentRow()], window=7))
        setQueryUsr.clicked.connect(lambda: self.window.close())
        closeWindow.clicked.connect(lambda: self.window.close())
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
        layout.addWidget(closeWindow, 9, 0, 1, 3)
        scroll.setWidget(scrollContent)

        self.window.show()
        self.window.move(self.gui.geometry().center() - self.window.rect().center())