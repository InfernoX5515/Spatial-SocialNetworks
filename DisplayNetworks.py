def displayRoadNetwork(root, network, graph):
    #root.clearView()

    root.graphs["Main Road Network"].clear()

    # Visualizes the graph that is being selected
    if network is not None:
        root.roadNetworks[network].visualize(root.graphs["Main Road Network"])


    # If the summary is not selected
    '''if not self.summarySelected:
        self.clearView()
        self.selectedRoadNetwork = None
        self.createPlots()
        # Display road network
        if network is not None:
            # Visualizes the graph that is being selected
            self.__roadNetworkObjs[network].visualize(self.roadGraphWidget)
            self.selectedRoadNetwork = self.__roadNetworkObjs[network]
        # Display social network
        if self.selectedSocialNetwork is not None:
            self.selectedSocialNetwork.visualize(self.socialGraphWidget, self.roadGraphWidget)
        self.plotQueryUser()
        self.linkGraphAxis()
    # If the summary is selected
    else:
        self.clearView()
        self.selectedRoadNetwork = None
        self.createSumPlot("Summary")
        # Display road network
        if network is not None:
            self.selectedRoadNetwork = self.__roadNetworkObjs[network]
            self.selectedRoadNetwork.visualize(self.roadGraphWidget)
        # Draw social network
        if self.selectedSocialNetwork is not None:
            centers, sizes, relations, popSize = self.getSummaryClusters(self.clusterInput.textBox.text())
            self.visualizeSummaryData(centers, sizes, relations, popSize)
        self.plotQueryUser()'''
        # self.linkGraphAxis()