from anytree import Node, RenderTree, find_by_attr
import PyQt5.QtWidgets as QtWidgets
from RoadNetwork import RoadNetwork


# Menu bar class for more simple management
from SummaryDisplay import viewSummary


class MenuBar:
    def __init__(self, menuBar):
        self.menu = menuBar
        self.menuTree = Node('root')
        self.__menuGroups = {}

    # Adds a dropdown to the menu
    def addMenu(self, name):
        menu = self.menu.addMenu(name)
        Node(name, obj=menu, parent=self.menuTree)

    # Adds a child to the menu's dropdowns
    def addChild(self, name, parent, shortcut=None, tooltip=None, action=None, group=None, checked=False):
        child = QtWidgets.QAction(name, self.menu)

        if shortcut is not None:
            child.setShortcut(shortcut)
        if tooltip is not None:
            child.setStatusTip(tooltip)
        if action is not None:
            child.triggered.connect(action)
        if group is not None:
            if group not in self.__menuGroups:
                raise Exception(f"Group '{group}' does not exist.")
            self.__menuGroups[group].addAction(child)
            child.setCheckable(True)
            child.setChecked(checked)

        parentNode = find_by_attr(self.menuTree, parent)
        if parentNode is None:
            raise Exception(f"Menu item '{parent}' was not found.")
        parentNode.obj.addAction(child)
        Node(name, obj=child, parent=parentNode)

    # Create a radio button group
    def createGroup(self, name, appRoot):
        if name in self.__menuGroups:
            raise Exception(f"Group '{name}' already exists.")
        self.__menuGroups[name] = QtWidgets.QActionGroup(appRoot)

    # Prints the menu's structure
    def printTree(self):
        print(RenderTree(self.menuTree))


# Display the menu bar on the window
def showMenuBar(root):
    menu = MenuBar(root.menuBar())

    menu.addMenu("File")
    from BuildNetworks import buildNetworkWindow
    menu.addChild("Files", "File", shortcut="Ctrl+f", tooltip="View files", action=lambda: root.openWindow(
        buildNetworkWindow(root)))

    menu.addMenu("View")
    menu.createGroup("ViewGroup", root)
    menu.addChild("Full View", "View", group="ViewGroup", tooltip="View full graphs", action=lambda: viewSummary(root),
                  checked=True)
    menu.addChild("Summary View", "View", group="ViewGroup", tooltip="View summary graphs",
                  action=lambda: viewSummary(root))

    networks = root.config.getCompleteNetworks()
    sNetworks = networks["Social Networks"]
    rNetworks = networks["Road Networks"]

    menu.addMenu("Social Networks")
    menu.createGroup("SocialNetworkGroup", root)
    menu.addChild("None", "Social Networks", group="SocialNetworkGroup", tooltip="Display no social network",
                  action=lambda j: root.displaySocialNetwork(None), checked=True)
    for x in sNetworks:
        menu.addChild(x, "Social Networks", group="SocialNetworkGroup",
                      tooltip=f"Switch to view social network {x}",
                      action=lambda j, a=x: root.displaySocialNetwork(a))

    menu.addMenu("Road Networks")
    menu.createGroup("RoadNetworkGroup", root)
    menu.addChild("None", "Road Networks", group="RoadNetworkGroup", tooltip="Display no road network",
                  action=lambda j: root.displayRoadNetwork(None), checked=True)
    for x in rNetworks:
        menu.addChild(x, "Road Networks", group="RoadNetworkGroup", tooltip=f"Switch to view road network {x}",
                      action=lambda j, a=x: root.displayRoadNetwork(a))

    root.menu = menu


def reloadMenu(root):
    root.menuBar().clear()
    oldRN = root.roadNetworks
    oldSN = root.socialNetworks

    showMenuBar(root)

    roadNetworks = root.config.settings["Road Networks"]
    socialNetworks = root.config.settings["Social Networks"]

    reloadRN = False
    for network in root.roadNetworks:
        if network not in oldRN and root.config.isComplete("road", network):
            reloadRN = True
    if reloadRN:
        root.roadNetworks = root.createNetworkInstances(root.roadNetworks, RoadNetwork)

    for network in root.socialNetworks:
        if network not in oldSN:
            root.__socialNetworkObjs[network] = root.config.getNewSocialNetwork(network)
