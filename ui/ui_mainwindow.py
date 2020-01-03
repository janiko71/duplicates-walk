# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 5.14.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(815, 531)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(760, 320))
        self.actionSortie = QAction(MainWindow)
        self.actionSortie.setObjectName(u"actionSortie")
        self.actionCouper = QAction(MainWindow)
        self.actionCouper.setObjectName(u"actionCouper")
        self.actionCopier = QAction(MainWindow)
        self.actionCopier.setObjectName(u"actionCopier")
        self.actionColler = QAction(MainWindow)
        self.actionColler.setObjectName(u"actionColler")
        self.actionSupprimer = QAction(MainWindow)
        self.actionSupprimer.setObjectName(u"actionSupprimer")
        self.actionNouvelle_recherche = QAction(MainWindow)
        self.actionNouvelle_recherche.setObjectName(u"actionNouvelle_recherche")
        self.actionOptions = QAction(MainWindow)
        self.actionOptions.setObjectName(u"actionOptions")
        self.actionSelection = QAction(MainWindow)
        self.actionSelection.setObjectName(u"actionSelection")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy1)
        self.centralwidget.setMinimumSize(QSize(145, 0))
        self.centralwidget.setSizeIncrement(QSize(0, 0))
        self.centralwidget.setLayoutDirection(Qt.LeftToRight)
        self.horizontalLayout_2 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tab_search = QWidget()
        self.tab_search.setObjectName(u"tab_search")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tab_search.sizePolicy().hasHeightForWidth())
        self.tab_search.setSizePolicy(sizePolicy2)
        self.horizontalLayout_3 = QHBoxLayout(self.tab_search)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.treeview_os_directories = QTreeView(self.tab_search)
        self.treeview_os_directories.setObjectName(u"treeview_os_directories")
        self.treeview_os_directories.setMinimumSize(QSize(300, 200))
        self.treeview_os_directories.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeview_os_directories.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_3.addWidget(self.treeview_os_directories)

        self.listWidget_selected_directories = QListWidget(self.tab_search)
        self.listWidget_selected_directories.setObjectName(u"listWidget_selected_directories")
        self.listWidget_selected_directories.setMinimumSize(QSize(400, 200))

        self.horizontalLayout_3.addWidget(self.listWidget_selected_directories)

        self.tabWidget.addTab(self.tab_search, "")
        self.tab_results = QWidget()
        self.tab_results.setObjectName(u"tab_results")
        self.horizontalLayout = QHBoxLayout(self.tab_results)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tabWidget.addTab(self.tab_results, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 815, 21))
        self.menuFichier = QMenu(self.menubar)
        self.menuFichier.setObjectName(u"menuFichier")
        self.menuEdition = QMenu(self.menubar)
        self.menuEdition.setObjectName(u"menuEdition")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setAutoFillBackground(True)
        self.toolBar.setMovable(False)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolBar.setFloatable(False)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFichier.menuAction())
        self.menubar.addAction(self.menuEdition.menuAction())
        self.menuFichier.addAction(self.actionNouvelle_recherche)
        self.menuFichier.addAction(self.actionOptions)
        self.menuFichier.addSeparator()
        self.menuFichier.addAction(self.actionSortie)
        self.menuEdition.addAction(self.actionCouper)
        self.menuEdition.addAction(self.actionCopier)
        self.menuEdition.addAction(self.actionColler)
        self.menuEdition.addAction(self.actionSupprimer)
        self.toolBar.addAction(self.actionNouvelle_recherche)
        self.toolBar.addAction(self.actionOptions)
        self.toolBar.addSeparator()

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSortie.setText(QCoreApplication.translate("MainWindow", u"Sortie", None))
#if QT_CONFIG(shortcut)
        self.actionSortie.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.actionCouper.setText(QCoreApplication.translate("MainWindow", u"Couper", None))
        self.actionCopier.setText(QCoreApplication.translate("MainWindow", u"Copier", None))
        self.actionColler.setText(QCoreApplication.translate("MainWindow", u"Coller", None))
        self.actionSupprimer.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.actionNouvelle_recherche.setText(QCoreApplication.translate("MainWindow", u"Nouvelle recherche", None))
#if QT_CONFIG(shortcut)
        self.actionNouvelle_recherche.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionOptions.setText(QCoreApplication.translate("MainWindow", u"Options", None))
#if QT_CONFIG(shortcut)
        self.actionOptions.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSelection.setText(QCoreApplication.translate("MainWindow", u"S\u00e9lectionner", None))
#if QT_CONFIG(tooltip)
        self.actionSelection.setToolTip(QCoreApplication.translate("MainWindow", u"S\u00e9lectionner", None))
#endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_search), QCoreApplication.translate("MainWindow", u"Recherche", None))
#if QT_CONFIG(whatsthis)
        self.tabWidget.setTabWhatsThis(self.tabWidget.indexOf(self.tab_search), QCoreApplication.translate("MainWindow", u"Fen\u00eatre contenant les param\u00e8tres de la recherche de doublons.", None))
#endif // QT_CONFIG(whatsthis)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_results), QCoreApplication.translate("MainWindow", u"R\u00e9sultats", None))
        self.menuFichier.setTitle(QCoreApplication.translate("MainWindow", u"Fichier", None))
        self.menuEdition.setTitle(QCoreApplication.translate("MainWindow", u"Edition", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

