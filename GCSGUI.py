from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from FingerTabs import *
from VipTabBar import VipTabBarWidget
from VipWidget import *

import sys, os
from aqua.qsshelper import QSSHelper


class GMapWebView(QWebView):

	def __init__(self, source):
		super(GMapWebView, self).__init__()
		file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), source))
		local_url = QUrl.fromLocalFile(file_path)
		self.load(local_url)

		self.frame = self.page().mainFrame()




class MainFrame(QWidget):

	def __init__(self):
		super(MainFrame, self).__init__()

		self.navBar = QVBoxLayout()
		self.stackedLayout = QStackedWidget()

		# self.mapBtn = QPushButton()
		# self.mapBtn.setIcon(QIcon('image/navi_white.png'))
		# self.mapBtn.setIconSize(QSize(130,130))
		# self.streamingBtn = QPushButton()
		# self.streamingBtn.setIcon(QIcon('image/video_white.png'))
		# self.streamingBtn.setIconSize(QSize(130,130))

		self.mapBtn = VipNavBarBtn(QIcon('image/navi_white.png'), QIcon('image/navi_hover.png'))
		self.streamingBtn = VipNavBarBtn(QIcon('image/video_white.png'), QIcon('image/video_hover.png'))
		self.Btn1 = VipNavBarBtn(QIcon('image/navi_white.png'), QIcon('image/navi_hover.png'))
		self.Btn2 = VipNavBarBtn(QIcon('image/video_white.png'), QIcon('image/video_hover.png'))
		self.mapBtn.setIconSize(QSize(110,110))
		self.streamingBtn.setIconSize(QSize(110,110))
		self.Btn1.setIconSize(QSize(110,110))
		self.Btn2.setIconSize(QSize(110,110))
		self.navBar.addWidget(self.mapBtn)
		self.navBar.addWidget(self.streamingBtn)
		self.navBar.addWidget(self.Btn1)
		self.navBar.addWidget(self.Btn2)

		# self.mapBtn.setWindowFlags(Qt.FramelessWindowHint)
		# self.mapBtn.setAttribute(Qt.WA_TranslucentBackground)

		""" remove margin and padding """
		self.navBar.setSpacing(0)
		self.navBar.setContentsMargins(0,0,0,0)


		self.navWidget = QWidget()
		self.navWidget.setLayout(self.navBar)
		self.navWidget.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			padding-top: 20px;
			margin: 0px;""")

		self.navBar.setAlignment(Qt.AlignTop)
		

		self.streamingBtn.clicked.connect(self.on_streaming_clicked)
		self.mapBtn.clicked.connect(self.on_map_clicked)

		
		self.gmapLayout = QGridLayout()
		self.gmap = GMapWebView("gmap-drone.html")
		self.logText = QTextEdit()
		self.logText.setReadOnly(True)
		self.logText.setText("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
		self.logText.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			border-color: rgb(255,255,255);
			color: white;
			padding: 3px;
			border: none;""")
		self.takeoffBtn = QPushButton("")
		self.takeoffBtn.setIcon(QIcon('image/takoff.png'))
		self.takeoffBtn.setIconSize(QSize(130,130))
		self.targetBtn = QPushButton("")
		self.targetBtn.setIcon(QIcon('image/target.png'))
		self.targetBtn.setIconSize(QSize(130,130))

		self.gmapLayout.addWidget(self.gmap, 0, 0, 2, 5)
		self.gmapLayout.addWidget(self.logText, 1, 4, 1, 1)
		self.gmapLayout.addWidget(self.takeoffBtn, 1, 1, 1, 1)
		self.gmapLayout.addWidget(self.targetBtn, 1, 2, 1, 1)

		self.gmapLayout.setColumnStretch(0, 1)
		self.gmapLayout.setColumnStretch(1, 1)
		self.gmapLayout.setColumnStretch(2, 1)
		self.gmapLayout.setColumnStretch(3, 1)
		self.gmapLayout.setColumnStretch(4, 2)
		self.gmapLayout.setRowStretch(0, 3)
		self.gmapLayout.setRowStretch(1, 1)
		self.gmapWidget = QWidget()
		self.gmapWidget.setLayout(self.gmapLayout)
		self.stackedLayout.addWidget(self.gmapWidget)

		self.streaming = QWidget()
		self.streaming.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			border-color: rgb(255,255,255);
			border: none;""")
		self.stackedLayout.addWidget(self.streaming)

		self.gridLayout = QGridLayout()
		self.gridLayout.addWidget(self.stackedLayout, 0, 0, 1, 2)
		self.gridLayout.addWidget(self.navWidget, 0, 0, 1, 1)
		self.gridLayout.setColumnStretch(0, 1)
		self.gridLayout.setColumnStretch(1, 10)

		self.setLayout(self.gridLayout)
		self.resize(2280, 1520)
		

	def on_map_clicked(self):
		print "clicked"
		self.stackedLayout.setCurrentIndex(0)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()
		# self.navBar.raise_()
		# self.stackedLayout.lower()
		# self.stackedLayout.setCurrentWidget(self.gmap)

	def on_streaming_clicked(self):
		print "clicked"
		self.stackedLayout.setCurrentIndex(1)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()
		# self.stackedLayout.lower()
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