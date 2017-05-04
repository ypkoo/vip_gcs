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

class MainFrame(QWidget):

	def __init__(self):
		super(MainFrame, self).__init__()

		self.navBar = QVBoxLayout()
		self.stackedLayout = QStackedLayout()

		self.mapBtn = QPushButton()
		self.mapBtn.setIcon(QIcon('image/navi_white.png'))
		self.mapBtn.setIconSize(QSize(130,130))
		self.streamingBtn = QPushButton()
		self.streamingBtn.setIcon(QIcon('image/video_white.png'))
		self.streamingBtn.setIconSize(QSize(130,130))
		self.navBar.addWidget(self.mapBtn)
		self.navBar.addWidget(self.streamingBtn)
		

		self.streamingBtn.clicked.connect(self.on_streaming_clicked)
		self.mapBtn.clicked.connect(self.on_map_clicked)

		self.navBar.addWidget(self.mapBtn)
		self.navBar.addWidget(self.streamingBtn)

		

		self.gmap = GMapWebView()
		self.stackedLayout.addWidget(self.gmap)

		self.streaming = QWidget()
		self.streaming.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			border-color: rgb(255,255,255);
			border: 3px solid rgb(255,255,255);""")
		self.stackedLayout.addWidget(self.streaming)

		self.gridLayout = QGridLayout()
		self.gridLayout.addLayout(self.stackedLayout, 0, 0, 10, 10)
		self.gridLayout.addLayout(self.navBar, 0, 0, 10, 1)

		self.setLayout(self.gridLayout)
		

	def on_map_clicked(self):
		print "clicked"
		self.stackedLayout.setCurrentIndex(0)
		self.navBar.raise_()
		# self.stackedLayout.setCurrentWidget(self.gmap)

	def on_streaming_clicked(self):
		print "clicked"
		self.stackedLayout.setCurrentIndex(1)
		self.navBar.raise_()
		# self.stackedLayout.setCurrentWidget(self.streaming)




if __name__ == '__main__':
	app = QApplication(sys.argv)
	# qss = QSSHelper.open_qss(os.path.join('aqua', 'aqua.qss'))
	style = QSSHelper.open_qss('style.qss')
	# app.setStyleSheet(qss + style)
	app.setStyleSheet(style)
	frame = MainFrame()
	frame.show()
	sys.exit(app.exec_())