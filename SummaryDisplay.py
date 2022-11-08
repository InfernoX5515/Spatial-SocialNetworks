from PyQt5.QtWebEngineWidgets import QWebEngineView
import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtGui, QtCore


# Creates graphs for summary layout
def createSummaryGraphs(layout):
    graphs = {"Summary Road Network": layout.addPlot(row=0, col=1, title=f"Road Network Summary")}
    return graphs


# Handles summary view
def viewSummary(root):
    # Switch view to summary if not already
    if "Summary Road Network" not in root.graphs:
        # Clear the window view
        root.clearView()

        # Setup summary view
        root.setupLayout()

        # Add interactive NetworkX social network graph
        socialNXWidget = QWebEngineView()
        with open('nx.html', 'r') as f:
            html = f.read()
            socialNXWidget.setHtml(html)

        root.window.layoutWidget.insertWidget(0, socialNXWidget)

        # Add the road network graph
        root.graphs = createSummaryGraphs(root.window.layoutWidget.layout)

        clusterToolbar(root)
        #root.__queryInput()
        #root.updateSummaryGraph()


# Creates the cluster toolbar for inputs
def clusterToolbar(root):
    # Set up input toolbar
    clusterToolbar = QtWidgets.QToolBar("clusterInput")
    root.addToolBar(clusterToolbar)

    clusterToolbar.setIconSize(QtCore.QSize(24, 24))

    # Create label
    nClustersLabel = QtWidgets.QLabel(text="n-clusters: ")

    # Create button
    submitButton = QtWidgets.QPushButton("Ok")
    #submitButton.clicked.connect(lambda: self.updateSummaryGraph())

    # Create text box
    clusterToolbar.textBox = QtWidgets.QLineEdit()
    clusterToolbar.textBox.setValidator(QtGui.QIntValidator(0, 9999))
    clusterToolbar.textBox.setText("10")
    clusterToolbar.textBox.returnPressed.connect(submitButton.click)

    # Add widgets to window
    clusterToolbar.addWidget(nClustersLabel)
    clusterToolbar.addWidget(clusterToolbar.textBox)
    clusterToolbar.addWidget(submitButton)

    toolbars = root.toolbars
    if toolbars is None:
        toolbars = {"Cluster Toolbar": clusterToolbar}
    else:
        toolbars["Cluster Toolbar"] = clusterToolbar
