from os import getenv
from PyQt5 import QtCore
import pyqtgraph as pg
import PyQt5.QtWidgets as QtWidgets
from anytree import Node, find_by_attr

tree = Node('root')


def buildNetworkWindow(root):
    global tree
    tree = Node('root')

    roadNetworks = root.config.settings["Road Networks"]
    socialNetworks = root.config.settings["Social Networks"]

    Node("Road Networks", obj=QtWidgets.QTreeWidgetItem(["Road Networks"]), parent=tree)
    Node("Social Networks", obj=QtWidgets.QTreeWidgetItem(["Social Networks"]), parent=tree)

    # Set up tree widget
    win = pg.TreeWidget()

    win.setWindowModality(QtCore.Qt.ApplicationModal)
    win.setDragEnabled(False)
    win.header().setSectionsMovable(False)
    win.header().setStretchLastSection(False)
    win.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    win.setWindowTitle('Network Files')
    win.setColumnCount(2)

    winW = int(root.frameGeometry().width() / 2)
    winH = int(root.frameGeometry().height() / 2)
    win.resize(winW, winH)

    win.show()

    # Add Road Networks and Social Networks to hierarchy
    win.addTopLevelItem(find_by_attr(tree, "Road Networks").obj)

    newRNButton = QtWidgets.QPushButton("Create a new Road Network")
    newRNButton.clicked.connect(lambda: newNetwork(root, win, "road"))
    win.setItemWidget(find_by_attr(tree, "Road Networks").obj, 1, newRNButton)

    win.addTopLevelItem(find_by_attr(tree, "Social Networks").obj)

    newSNButton = QtWidgets.QPushButton("Create a new Social Network")
    newSNButton.clicked.connect(lambda: newNetwork(root, win, "social"))
    win.setItemWidget(find_by_attr(tree, "Social Networks").obj, 1, newSNButton)

    for network in roadNetworks:
        parent = find_by_attr(tree, "Road Networks")
        child = Node(f"{network}", obj=QtWidgets.QTreeWidgetItem([network]), parent=parent)
        parent.obj.addChild(child.obj)

        parent = child

        i = 0
        # Adds files
        cFile = {}
        for item in roadNetworks[network]:
            i += 1
            iName = roadNetworks[network][item]
            if iName != f"[{iName}]":
                iNameArr = iName.split("/")
                iName = iNameArr[len(iNameArr) - 1]

            child = Node(f"{item}", obj=QtWidgets.QTreeWidgetItem([iName]), parent=parent)
            parent.obj.addChild(child.obj)
            cFile[i] = QtWidgets.QPushButton(f"Choose Directory")
            cFile[i].clicked.connect(lambda j, _item=item: chooseFile(root, "road", _item, roadNetworks, network))
            win.setItemWidget(child.obj, 1, cFile[i])

    for network in socialNetworks:
        parent = find_by_attr(tree, "Social Networks")
        child = Node(f"{network}", obj=QtWidgets.QTreeWidgetItem([network]), parent=parent)
        parent.obj.addChild(child.obj)

        parent = child

        i = 0
        # Adds files
        cFile = {}
        for item in socialNetworks[network]:
            i += 1
            iName = socialNetworks[network][item]
            if iName != f"[{iName}]":
                iNameArr = iName.split("/")
                iName = f"{iNameArr[len(iNameArr) - 1]}/"

            child = Node(f"{item}", obj=QtWidgets.QTreeWidgetItem([iName]), parent=parent)
            parent.obj.addChild(child.obj)
            cFile[i] = QtWidgets.QPushButton("Choose Directory")
            cFile[i].clicked.connect(lambda j, _item=item: chooseFile(root, "social", _item, socialNetworks, network))
            win.setItemWidget(child.obj, 1, cFile[i])
    return win


# Creates a new network
def newNetwork(root, winParent, type):
    title = ""

    if type == "road":
        existing = root.config.settings["Road Networks"]
        title = "Road Network"
    elif type == "social":
        existing = root.config.settings["Social Networks"]
        title = "Social Network"
    else:
        raise Exception("ERROR: newNetwork() must have type 'road' or 'social'")

    win = QtWidgets.QInputDialog()
    text, ok = win.getText(root, f'New {title}', f"Enter your {title.lower()} name:")
    text = str(text)

    # If the road network does not exist already, add it to the config
    if ok and text not in existing and text != "":
        print(existing)
        if type == "road":
            existing[text] = {
                "Path": "[Path]"
            }
        elif type == "social":
            existing[text] = {
                "Path": "[Path]"
            }

        # Adds new network to tree
        keys = list(existing.keys())

        # Add new network to hierarchy
        parent = find_by_attr(tree, f"{title}s")
        child = Node(f"{text}", obj=QtWidgets.QTreeWidgetItem([text]), parent=parent)

        parent.obj.addChild(child.obj)

        parent = child

        for i in existing[text]:
            child = Node(f"{i}", obj=QtWidgets.QTreeWidgetItem([i]), parent=parent)
            parent.obj.addChild(child.obj)
            if type == "road":
                chooseFileButton = QtWidgets.QPushButton(f"Choose {i} File")
            elif type == "social":
                chooseFileButton = QtWidgets.QPushButton(f"Choose Directory")
            else:
                raise Exception("ERROR: newNetwork() must have type 'road' or 'social'")
            chooseFileButton.clicked.connect(lambda j, _i=i: chooseFile(root, type, f"{_i}", existing, text))
            winParent.setItemWidget(child.obj, 1, chooseFileButton)
        # Update config
        root.config.update(f"{title}s", existing)


def chooseFile(root, type, selectType, networks, network):
    win = QtWidgets.QFileDialog()

    path = win.getExistingDirectory(None, f'Select {selectType}', getenv('HOME'))

    if len(path) != 0:
        networks[network][selectType] = path

        if type == "road":
            root.config.update("Road Networks", networks)

            # Update item
            fileNameArr = path.split("/")
            fileName = fileNameArr[len(fileNameArr) - 1]
            rnNode = find_by_attr(tree, 'Road Networks')
            find_by_attr(find_by_attr(rnNode, f"{network}"), f"{selectType}").obj.setText(0, f"{fileName}/")
        elif type == "social":
            root.config.update("Social Networks", networks)

            # Update item
            fileNameArr = path.split("/")
            fileName = fileNameArr[len(fileNameArr) - 1]
            snNode = find_by_attr(tree, 'Social Networks')
            find_by_attr(find_by_attr(snNode, f"{network}"), f"{selectType}").obj.setText(0, f"{fileName}/")
        else:
            raise Exception("ERROR: chooseFile() must have type 'road' or 'social'")
    from MenuBar import reloadMenu
    reloadMenu(root)

