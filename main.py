import io, sys
import sqlite3

from PySide2.QtWidgets import QAction, QApplication, QFileSystemModel, QListWidgetItem, QMainWindow, QMenu
from PySide2.QtCore import QDir, Qt
from PySide2.QtGui import QStandardItemModel

import ui.ui_mainwindow as ui

global dir_list

class AppUI(QMainWindow, ui.Ui_MainWindow):

    #
    # Qt-derived class for Application UI
    #

    def __init__(self):

        QMainWindow.__init__(self)
        self.setupUi(self)

        # Viewing the filesystem tree

        treeModel = QFileSystemModel()
        treeModel.setRootPath(QDir.currentPath())

        # We only show the name/path

        view = self.treeview_os_directories 
        view.setModel(treeModel)
        view.model().sort(1, order=Qt.DescendingOrder)
        view.hideColumn(1)
        view.hideColumn(2)
        view.hideColumn(3)
        view.setColumnWidth(0, 10)
        view.setColumnWidth(1, 1)
        view.setColumnWidth(2, 1)

        # Setting a contextual menu

        self.treeview_os_directories.customContextMenuRequested.connect(self.openMenuDirectories)

        # Adding actions

        self.actionSortie.triggered.connect(self.close)

        # The selected directories/files (search list) will be stored in a global list

        global dir_list

        for dir in dir_list:
            self.listWidget_selected_directories.addItem(QListWidgetItem(dir))



    def openMenuDirectories(self, position):

        #
        # Contextual menu for the filesystem tree view
        #

        menu_os_directories = QMenu()

        menu_add = QAction("Ajouter")
        menu_add.triggered.connect(self.addDirectory)
        menu_os_directories.addAction(menu_add)
        menu_dvlp = QAction("Développer")
        menu_os_directories.addAction(menu_dvlp)
        menu_ref = QAction("Actualiser")
        menu_os_directories.addAction(menu_ref)

        menu_os_directories.exec_(self.treeview_os_directories.viewport().mapToGlobal(position))


    def addDirectory(self):

        # 
        # Adding the selected item (path, file) in the search list
        #

        global dir_list

        sel_dir = self.treeview_os_directories.selectedIndexes()

        for dir in sel_dir:
            dir_list.append(self.treeview_os_directories.model().filePath(dir))
            #self.listWidget_selected_directories.addItem(self.treeview_os_directories.model().filePath(dir))
            #tableWidget_selected_directories



if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Global search list

    dir_list = []

    # Show main window

    wind = AppUI()
    wind.show()
    
    # Exec Qt Application

    app.exec_()
