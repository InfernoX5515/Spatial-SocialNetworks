from os import getenv

from PyQt5 import QtGui, QtCore
import pyqtgraph as pg
import PyQt5.QtWidgets as QtWidgets
from anytree import Node, RenderTree, find_by_attr


tree = Node('root')


def buildNetworkWindow(root, winW, winH, roadNetworks, socialNetworks, config, reloadMenuFunc):
    global tree
    tree = Node('root')

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
    win.resize(winW, winH)

    win.show()

    # Add Road Networks and Social Networks to hierarchy
    win.addTopLevelItem(find_by_attr(tree, "Road Networks").obj)

    newRNButton = QtWidgets.QPushButton("Create a new Road Network")
    newRNButton.clicked.connect(lambda: newNetwork(root, win, "road", roadNetworks, config, reloadMenuFunc))
    win.setItemWidget(find_by_attr(tree, "Road Networks").obj, 1, newRNButton)

    win.addTopLevelItem(find_by_attr(tree, "Social Networks").obj)

    newSNButton = QtWidgets.QPushButton("Create a new Social Network")
    newSNButton.clicked.connect(lambda: newNetwork(root, win, "social", socialNetworks, config, reloadMenuFunc))
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
            cFile[i] = QtWidgets.QPushButton(f"Choose {item} File")
            cFile[i].clicked.connect(lambda j, _item=item: chooseFile("road", _item, config, reloadMenuFunc, roadNetworks,
                                                                      network))
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

            child = Node(f"{item}", obj=QtWidgets.QTreeWidgetItem([iName]),
                         parent=parent)
            parent.obj.addChild(child.obj)
            cFile[i] = QtWidgets.QPushButton("Choose Directory")
            cFile[i].clicked.connect(lambda j, _item=item: chooseFile("social", _item, config, reloadMenuFunc, socialNetworks,
                                                                      network))
            win.setItemWidget(child.obj, 1, cFile[i])
    return win


# Creates a new network
def newNetwork(root, winParent, type, existing, config, reloadMenuFunc):
    if type != "road" and type != "social":
        raise Exception("ERROR: newNetwork() must have type 'road' or 'social'")
    title = ""

    if type == "road":
        title = "Road Network"
    elif type == "social":
        title = "Social Network"

    win = QtWidgets.QInputDialog()
    text, ok = win.getText(root, f'New {title}', f"Enter your {title.lower()} name:")
    text = str(text)

    # If the road network does not exist already, add it to the config
    if ok and text not in existing and text != "":
        if type == "road":
            existing[text] = {
                "nodeFile": "[nodeFile]",
                "edgeFile": "[edgeFile]",
                "POIFile": "[POIFile]",
                "keyFile": "[keyFile]",
                "keyMapFile": "[keyMapFile]"
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
            chooseFileButton.clicked.connect(lambda j, _i=i: chooseFile(type, f"{_i}", config, reloadMenuFunc, existing, text))
            winParent.setItemWidget(child.obj, 1, chooseFileButton)
        # Update config
        config.update(f"{title}s", existing)


def chooseFile(type, selectType, config, reloadMenuFunc, networks, network):
    win = QtWidgets.QFileDialog()

    if type == "road":
        path = win.getOpenFileName(None, f'Select {selectType}', getenv('HOME'), "csv(*.csv)")[0]
    elif type == "social":
        path = win.getExistingDirectory(None, f'Select {selectType}', getenv('HOME'))
    else:
        raise Exception("ERROR: chooseFile() must have type 'road' or 'social'")

    if len(path) != 0:
        networks[network][selectType] = path

        if type == "road":
            config.update("Road Networks", networks)

            # Update item
            fileNameArr = path.split("/")
            fileName = fileNameArr[len(fileNameArr) - 1]
            rnNode = find_by_attr(tree, 'Road Networks')
            find_by_attr(find_by_attr(rnNode, f"{network}"), f"{selectType}").obj.setText(0, fileName)
        elif type == "social":
            config.update("Social Networks", networks)

            # Update item
            fileNameArr = path.split("/")
            fileName = fileNameArr[len(fileNameArr) - 1]
            snNode = find_by_attr(tree, 'Social Networks')
            find_by_attr(find_by_attr(snNode, f"{network}"), f"{selectType}").obj.setText(0, f"{fileName}/")
        else:
            raise Exception("ERROR: chooseFile() must have type 'road' or 'social'")
    reloadMenuFunc()

