from anytree import Node, RenderTree, find_by_attr
from PyQt5 import QtWidgets

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