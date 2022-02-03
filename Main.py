import sys
from pyqtgraph.Qt import QtGui
from GUI import Gui

# =====================================================================================================================
#
#   Author: Halie Eckert
#   Mentor: Dr. Xiang Lain
#   Date: 11/3/2021
#   SPATIAL-SOCIAL NETWORKS
#
#   "Efficient and Effective Management and Analytics Over Spatial-Social Networks"
#
#   Location-based social networks have grown in size and popularity in the past two decades due to their real-world
#   versatility. In such networks, it is important to create a spatial-social network that not only looks into
#   personal relationships among users but also their geographical closeness on real networks. In this project,
#   we look into how to efficiently and effectively manage as well as analyze these types of networks. To do this, we
#   design and build a system for managing, querying, and visualizing spatial-social networks. We will test and
#   evaluate the efficiency and effectiveness of this system by processing real-world and synthetic data sets.
#
# =====================================================================================================================


# TODO: Figure out why the heck this won't actually close when the GUI is closed
def main():
    # noinspection PyUnresolvedReferences
    app = QtGui.QApplication(sys.argv)
    gui = Gui()
    sys.exit(app.exec_())


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    main()
