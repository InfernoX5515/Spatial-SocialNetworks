from anytree import Node, RenderTree, find_by_attr
import PyQt5.QtWidgets as QtWidgets


# Menu bar class for more simple management
class MenuBar:
    def __init__(self, menuBar):
        self.menu = menuBar
        self.menuTree = Node('root')
        self.__menuGroups = {}

    def addMenu(self, name):
        menu = self.menu.addMenu(name)
        Node(name, obj=menu, parent=self.menuTree)

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

    def createGroup(self, name, appRoot):
        if name in self.__menuGroups:
            raise Exception(f"Group '{name}' already exists.")
        self.__menuGroups[name] = QtWidgets.QActionGroup(appRoot)

    def printTree(self):
        print(RenderTree(self.menuTree))


def buildMenuBar(root):
    menu = MenuBar(root.menuBar())

    menu.addMenu("File")
    menu.addChild("Files", "File", shortcut="Ctrl+f", tooltip="View files", action=root.viewFiles)

    menu.addMenu("View")
    menu.createGroup("ViewGroup", root)
    menu.addChild("Summary View", "View", group="ViewGroup", tooltip="View summary graphs", action=root.viewSummary)
    menu.addChild("Full View", "View", group="ViewGroup", tooltip="View full graphs", action=root.viewSummary,
                  checked=True)

    networks = root.getCompleteNetworks()
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
        menu.addChild(x, "Road Networks", group="RoadNetworkGroup",
                      tooltip=f"Switch to view road network {x}",
                      action=lambda j, a=x: root.displayRoadNetwork(a))

    menu.addMenu("Query")
    menu.addChild("kd-truss", "Query", tooltip="kd-truss menu", action=root.__queryInput)