# TODO: Fix issue where graph is squished
def jogLeftTool(self):
    xRanges = self.roadGraphWidget.getAxis('bottom').range
    xScale = (abs(xRanges[1] - xRanges[0]) * .25) / 2

    self.roadGraphWidget.setXRange(
        xRanges[0] + xScale, xRanges[1] + xScale)

# TODO: Fix issue where graph is squished
def jogRightTool(self):
    xRanges = self.roadGraphWidget.getAxis('bottom').range
    scale = (abs(xRanges[0]) - abs(xRanges[1]) - \
                 (abs(xRanges[0]) - abs(xRanges[1])) * 0.75) / 2
    self.roadGraphWidget.setXRange(xRanges[0] - scale, xRanges[1] - scale)

    # TODO: Fix issue where graph is squished
def jogUpTool(self):
    yRanges = self.roadGraphWidget.getAxis('left').range
    scale = (abs(yRanges[0]) - abs(yRanges[1]) - \
                 (abs(yRanges[0]) - abs(yRanges[1])) * 0.75) / 2
    self.roadGraphWidget.setYRange(yRanges[0] + scale, yRanges[1] + scale)

# TODO: Fix issue where graph is squished
def jogDownTool(self):
    yRanges = self.roadGraphWidget.getAxis('left').range
    scale = (abs(yRanges[0]) - abs(yRanges[1]) - \
                 (abs(yRanges[0]) - abs(yRanges[1])) * 0.75) / 2
    self.roadGraphWidget.setYRange(yRanges[0] - scale, yRanges[1] - scale)
