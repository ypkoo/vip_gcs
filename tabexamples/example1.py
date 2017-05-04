from PyQt4 import QtGui

def __init__(self, parent=None):
        """Constructor."""
        super(MyWidget, self).__init__(parent)

        # ---- filter widget

        #self._filter = QtGui.QLineEdit()

        # ---- define the model & views

        # model
        self._model = QtGui.QStandardItemModel()

        # filtering
        #self._filterModel = QtGui.QSortFilterProxyModel()
        #self._filterModel.setSourceModel(self._model)
        #self._filterModel.setDynamicSortFilter(True)
        #self._filterModel.setFilterKeyColumn(-1)
        #self._filterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # tree view
        self._tree = QtGui.QTreeView()
        self._tree.setModel(self._model)
        #self._tree.setModel(self._filterModel)
        self._tree.header().setStretchLastSection(False)

        # list view
        self._list = QtGui.QListView()
        self._list.setModel(self._model)
        #self._list.setModel(self._filterModel)

        # table view
        self._table = QtGui.QTableView()
        self._table.setModel(self._model)
        #self._table.setModel(self._filterModel)

        # ---- construct the tab widget with the views

        self._tabs = QtGui.QTabWidget()
        self._tabs.addTab(self._tree, 'Tree View')
        self._tabs.addTab(self._table, 'Table View')
        self._tabs.addTab(self._list, 'List View')
        #self._tabs.setCornerWidget(self._filter)

        # ---- bottom buttons

        self._addColumnButton = QtGui.QPushButton('Add Column')
        self._addRowButton = QtGui.QPushButton('Add Row')
        self._addChildButton = QtGui.QPushButton('Add Child')

        closeButton = QtGui.QPushButton('Close')

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonLayout.setSpacing(10)
        buttonLayout.addWidget(self._addColumnButton)
        buttonLayout.addWidget(self._addRowButton)
        buttonLayout.addWidget(self._addChildButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(closeButton)
        
        # ---- layout all the components

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.addWidget(self._tabs)
        layout.addLayout(buttonLayout)

        # you can explicitly set the layout this way in order to make the
        # widget actually display its contents. Alternatively, you can 
        # pass 'self' to the layout constructor.
        self.setLayout(layout)

        # just do some initial setup to populate data
        for i in range(0, 3):
            self._addColumn()

        for i in range(0, 3):
            self._addRow()
            self._addChild()
            self._addChild()

        # ---- connect all the signals

        self._addColumnButton.clicked.connect(self._addColumn)
        self._addRowButton.clicked.connect(self._addRow)
        self._addChildButton.clicked.connect(self._addChild)
        #self._filter.textChanged.connect(self._filterModel.setFilterWildcard)
        closeButton.clicked.connect(QtCore.QCoreApplication.quit)

    # -------------------------------------------------------------------------
    # Private functions:
    # -------------------------------------------------------------------------