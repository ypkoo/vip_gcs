from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from FingerTabs import *
from VipTabBar import VipTabBarWidget

import sys, os
from aqua.qsshelper import QSSHelper


class GMapWebView(QWebView):

	def __init__(self):
		super(GMapWebView, self).__init__()
		file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gmap-drone.html"))
		local_url = QUrl.fromLocalFile(file_path)
		self.load(local_url)

		self.frame = self.page().mainFrame()


class HoverQWidget(QWidget):
	def __init__(self):
		super(HoverQWidget, self).__init__()
		self.setMouseTracking(True)

	def enterEvent(self,event):
		print("Enter")
		self.setStyleSheet("""
			background-color:#45b545;
			border-bottom: 5px solid rgb(255,255,255);""")

	def leaveEvent(self,event):
		self.setStyleSheet("background-color:yellow;")
		print("Leave")

class MainFrame(QTabWidget):


	def __init__(self):
		super(MainFrame, self).__init__()

		
		
		self.setTabBar(VipTabBarWidget(width=100,height=25))

		self.tab1 = QWidget()
		self.tab2 = QWidget()

		self.addTab(self.tab1, "")
		self.addTab(self.tab2, "")
		self.setTabIcon(0, QIcon('image/navi_white_rotated.png'))
		self.setTabIcon(1, QIcon('image/video_white_rotated.png'))
		self.setIconSize(QSize(100,100))

		self.setTabPosition(QTabWidget.West)


		self.tab1UI()
		self.tab2UI()

		self.resize(2280, 1520)




	def tab1UI(self):


		self.gmap = GMapWebView()
		self.cmdLayout = QHBoxLayout()
		self.takeoffBtn = QPushButton("")
		self.takeoffBtn.setIcon(QIcon('image/takoff.png'))
		self.takeoffBtn.setIconSize(QSize(130,130))
		self.targetBtn = QPushButton("")
		self.targetBtn.setIcon(QIcon('image/target.png'))
		self.targetBtn.setIconSize(QSize(130,130))
		# self.btn.setWindowFlags(Qt.FramelessWindowHint)
		# self.btn.setAttribute(Qt.WA_TranslucentBackground)

		self.logText = QTextEdit()
		self.logText.setReadOnly(True)

		""" Transparent """
		# self.logText.setWindowFlags(Qt.FramelessWindowHint)
		# self.logText.setAttribute(Qt.WA_TranslucentBackground)
		self.logText.setText("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
		self.logText.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			border-color: rgb(255,255,255);
			border: 3px solid rgb(255,255,255);""")

		self.cmdLayout.addWidget(self.targetBtn)
		self.cmdLayout.addWidget(self.takeoffBtn)


		self.grid = QGridLayout()
		
		# self.grid.addWidget(self.gmap, 0, 1, 1, 10)
		# self.grid.addWidget(self.logText, 1, 1, 1, 10)
		# self.grid.addWidget(self.btn, 0, 1, 1, 1)

		self.grid.addWidget(self.gmap, 0, 0, 12, 3)
		self.grid.addWidget(self.logText, 10, 2, 2, 1)
		# self.grid.addWidget(self.btn, 0, 0, 1, 1)
		# self.grid.addWidget(self.takeoffBtn, 10, 0, 1, 1)
		# self.grid.addWidget(self.targetBtn, 10, 1, 1, 1)
		self.grid.addLayout(self.cmdLayout, 10, 0, 1, 1)
		
		self.grid.setColumnStretch(0, 1)
		self.grid.setColumnStretch(1, 6)
		self.grid.setColumnStretch(2, 4)

		# self.grid.setRowStretch(0, 10)
		# self.grid.setRowStretch(1, 20)

		# main_frame = QWidget()
		self.cmdLayout.setAlignment(Qt.AlignTop)
		self.tab1.setLayout(self.grid)

		# self.setCentralWidget(main_frame)
	

	def tab2UI(self):
		layout = QFormLayout()
		sex = QHBoxLayout()
		sex.addWidget(QRadioButton("Male"))
		sex.addWidget(QRadioButton("Female"))
		layout.addRow(QLabel("Sex"),sex)
		layout.addRow("Date of Birth",QLineEdit())
		# self.setTabText(1,"Personal Details")

		self.tab2.setLayout(layout)





if __name__ == '__main__':
	app = QApplication(sys.argv)
	# qss = QSSHelper.open_qss(os.path.join('aqua', 'aqua.qss'))
	style = QSSHelper.open_qss('style.qss')
	# app.setStyleSheet(qss + style)
	app.setStyleSheet(style)
	frame = MainFrame()
	frame.show()
	sys.exit(app.exec_())