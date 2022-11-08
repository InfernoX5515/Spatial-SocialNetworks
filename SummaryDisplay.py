from PyQt5.QtWebEngineWidgets import QWebEngineView
import PyQt5.QtWidgets as QtWidgets


# Creates graphs for summary layout
def createSummaryGraphs(layout):
    graphs = {"Summary Road Network": layout.addPlot(row=0, col=1, title=f"Road Network Summary")}
    return graphs


# Handles summary view
def viewSummary(root):
    # Switch view to summary
    #if not root.summarySelected:
    #root.summarySelected = True

    # Clear the window view
    root.clearView()

    # Setup summary view
    #root.window = QtWidgets.QWidget()
    #root.sumLayout = QtWidgets.QHBoxLayout()
    root.setupLayout()

    # Add interactive NetworkX social network graph
    socialNXWidget = QWebEngineView()
    with open('nx.html', 'r') as f:
        html = f.read()
        socialNXWidget.setHtml(html)

    root.window.layoutWidget.insertWidget(0, socialNXWidget)

    # Add the road network graph
    root.graphs = createSummaryGraphs(root.window.layoutWidget.layout)

    #root.sumLayout.addWidget(root.window.layoutWidget.layout, 50)
    #root.window.setLayout(root.sumLayout)
    #root.setCentralWidget(root.window)
    #root.__clusterInput()
    #root.__queryInput()
    #root.updateSummaryGraph()
    # Switch view to main
    '''else:
        # Setup default view
        root.window = QtWidgets.QWidget()
        root.window.layoutWidget = QtWidgets.QHBoxLayout()
        root.window.layoutWidget.addWidget(root.window.layoutWidget.layout)
        root.window.setLayout(root.window.layoutWidget)
        root.setCentralWidget(root.window)
        root.summarySelected = False
        root.clusterInput.close()
        root.clearView()
        root.queryInput.close()
        root.createPlots()
        # Re-visualize selected networks
        if root.selectedRoadNetwork is not None:
            root.selectedRoadNetwork.visualize(root.roadGraphWidget)
        if root.selectedSocialNetwork is not None:
            root.selectedSocialNetwork.visualize(root.socialGraphWidget, root.roadGraphWidget)
            root.plotQueryUser()'''
