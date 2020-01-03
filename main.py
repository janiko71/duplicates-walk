import io, sys

from PySide2.QtWidgets import QApplication, QFileSystemModel, QMainWindow, QMenu

import qt.ui_mainwindow as mw
from PySide2.QtCore import QDir


class AppUI(QMainWindow, mw.Ui_MainWindow):

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


    def openMenuDirectories(self, position):

        menu_os_directories = QMenu()

        menu_os_directories.addAction(self.tr("Edit person"))
        menu_os_directories.addAction(self.tr("Edit object/container"))
        menu_os_directories.addAction(self.tr("Edit object"))

        indexes = self.treeview_os_directories.selectedIndexes()
        menu_os_directories.exec_(self.treeview_os_directories.viewport().mapToGlobal(position))



if __name__ == "__main__":

    app = QApplication(sys.argv)
    
    wind = AppUI()
    wind.show()
    
    app.exec_()
