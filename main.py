import io, sys

from PySide2.QtWidgets import QAction, QApplication, QFileSystemModel, QListWidgetItem, QMainWindow, QMenu
from PySide2.QtCore import QDir
from PySide2.QtGui import QStandardItemModel

import ui.ui_mainwindow as ui

global dir_list

class AppUI(QMainWindow, ui.Ui_MainWindow):

    def __init__(self):

        QMainWindow.__init__(self)
        self.setupUi(self)

        treeModel = QFileSystemModel()
        treeModel.setRootPath(QDir.currentPath())

        self.treeview_os_directories.setModel(treeModel)
        self.treeview_os_directories.hideColumn(1)
        self.treeview_os_directories.hideColumn(2)
        self.treeview_os_directories.hideColumn(3)

        self.treeview_os_directories.customContextMenuRequested.connect(self.openMenuDirectories)

        self.actionSortie.triggered.connect(self.close)

        global dir_list

        for dir in dir_list:
            self.listWidget_selected_directories.addItem(QListWidgetItem(dir))



    def openMenuDirectories(self, position):

        menu_os_directories = QMenu()

        menu_add = QAction("Ajouter")
        menu_os_directories.addAction(menu_add)
        menu_dvlp = QAction("Développer")
        menu_os_directories.addAction(menu_dvlp)
        menu_ref = QAction("Actualiser")
        menu_os_directories.addAction(menu_ref)

        menu_os_directories.exec_(self.treeview_os_directories.viewport().mapToGlobal(position))



if __name__ == "__main__":

    app = QApplication(sys.argv)

    dir_list = []
    dir_list.append("D:\\tests")
    dir_list.append("C:\\Users\\Janiko\\OneDrive\\Dev")

    wind = AppUI()
    wind.show()
    
    app.exec_()
