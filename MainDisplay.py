# Displays main window
from PyQt5 import QtWidgets


def createMainGraphs(layout):
    graphs = {"Main Road Network": layout.addPlot(row=0, col=1, title=f"Road Network"),
              "Main Social Network": layout.addPlot(row=0, col=0, title=f"Social Network")}
    return graphs


def createQueryToolbar(root):
    # Set up input toolbar
    queryUserToolbar = QtWidgets.QToolBar("queryToolbar")
    root.addToolBar(queryUserToolbar)

    # Create button
    queryUserButton = QtWidgets.QPushButton("Select Query User")
    #queryUserButton.clicked.connect(lambda: self.chooseKeywordsMenu())
    queryKeywordButton = QtWidgets.QPushButton("Select Query Keyword")
    #queryKeywordButton.clicked.connect(lambda: self.chooseQueryKeywordMenu())

    # Create label
    queryUserLabel = QtWidgets.QLabel("  Query User: ")
    queryKeywordLabel = QtWidgets.QLabel("  Query Keyword: ")

    if root.queryUser is not None:
        queryUserToolbar.userLabel = QtWidgets.QLabel(root.queryUser[0].split(".0")[0])
    else:
        queryUserToolbar.userLabel = QtWidgets.QLabel("None")
    if root.queryKeyword is not None:
        queryUserToolbar.keywordLabel = QtWidgets.QLabel(root.queryKeyword)
    else:
        queryUserToolbar.keywordLabel = QtWidgets.QLabel("None")
    # Add widgets to window
    queryUserToolbar.addWidget(queryUserButton)
    queryUserToolbar.addWidget(queryUserLabel)
    queryUserToolbar.addWidget(queryUserToolbar.userLabel)
    queryUserToolbar.addWidget(QtWidgets.QLabel("          "))
    queryUserToolbar.addWidget(queryKeywordButton)
    queryUserToolbar.addWidget(queryKeywordLabel)
    queryUserToolbar.addWidget(queryUserToolbar.keywordLabel)