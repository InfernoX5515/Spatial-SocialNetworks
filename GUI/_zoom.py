

def zoomOutTool(self):
    xRanges = self.roadGraphWidget.getAxis('bottom').range
    yRanges = self.roadGraphWidget.getAxis('left').range
    xScale, yScale = self.getZoomScale(xRanges, yRanges)
    self.roadGraphWidget.setXRange(xRanges[0] - xScale, xRanges[1] + xScale)
    self.roadGraphWidget.setYRange(yRanges[0] - yScale, yRanges[1] + yScale)

def zoomInTool(self):
    xRanges = self.roadGraphWidget.getAxis('bottom').range
    yRanges = self.roadGraphWidget.getAxis('left').range
    xScale, yScale = self.getZoomScale(xRanges, yRanges)
    self.roadGraphWidget.setXRange(xRanges[0] + xScale, xRanges[1] - xScale)
    self.roadGraphWidget.setYRange(yRanges[0] + yScale, yRanges[1] - yScale)