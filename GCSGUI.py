from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from VipWidget import *
from GCSServer import *

import sys, os, time, signal
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

		self.frame_init()
		self.gcs_server_init()
		
	
	def frame_init(self):
		self.navBar = VipNavBar()
		self.stackedLayout = QStackedWidget()

		self.mapBtn = VipNavBarBtn(
			icon_default = QIcon('image/navi_white.png'),
			icon_hover = QIcon('image/navi_hover.png'),
			icon_others_hover = QIcon('image/map.png'))
		self.streamingBtn = VipNavBarBtn(
			icon_default = QIcon('image/video_white.png'),
			icon_hover = QIcon('image/video_hover.png'),
			icon_others_hover = QIcon('image/video.png'))
		self.Btn1 = VipNavBarBtn(
			icon_default = QIcon('image/navi_white.png'),
			icon_hover = QIcon('image/navi_hover.png'),
			icon_others_hover = QIcon('image/map.png'))
		self.Btn2 = VipNavBarBtn(
			icon_default = QIcon('image/video_white.png'),
			icon_hover = QIcon('image/video_hover.png'),
			icon_others_hover = QIcon('image/video.png'))
		
		self.navBar.add_btn(self.mapBtn)
		self.navBar.add_btn(self.streamingBtn)

		self.droneStatusLayout = VipStatusLayout()
		# self.droneStatusLable1 = QLabel()
		# self.droneStatusLable2 = QLabel()
		# self.droneStatusLable1.setWordWrap(True)
		# self.droneStatusLable1.setText("testtestseaaaaaaaaaaaaaaaaaaa\natasdfasdfl;aksdjf;laskdjfl;askdf")
		# self.droneStatusLayout.add(self.droneStatusLable1)
		# self.droneStatusLayout.add(self.droneStatusLable2)

		self.textCommandLayout = VipTextCommandLayout()
		self.textCommandLayout.commandBtn.clicked.connect(self.on_textcommand_clicked)

		
		self.streamingBtn.clicked.connect(self.on_streaming_clicked)
		self.mapBtn.clicked.connect(self.on_map_clicked)

		
		self.gmapLayout = QGridLayout()
		self.gmap = GMapWebView("gmap-drone.html")
		self.logText = QTextEdit()
		self.logText.setReadOnly(True)
		
		self.logText.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			padding: 3px;
			margin-right: 20px;
			margin-bottom: 10px;
			border: none;""")
		self.takeoffBtn = QPushButton("")
		self.takeoffBtn.setIcon(QIcon('image/takoff.png'))
		self.takeoffBtn.setIconSize(QSize(130,130))
		self.targetBtn = QPushButton("")
		self.targetBtn.setIcon(QIcon('image/target.png'))
		self.targetBtn.setIconSize(QSize(130,130))

		self.takeoffBtn.clicked.connect(self.on_takeoff_clicked)

		# self.gmapLayout.addWidget(self.gmap, 0, 0, 2, 5)
		# self.gmapLayout.addWidget(self.logText, 1, 4, 1, 1)
		# self.gmapLayout.addWidget(self.takeoffBtn, 1, 1, 1, 1)
		# self.gmapLayout.addWidget(self.targetBtn, 1, 2, 1, 1)

		self.gmapLayout.addWidget(self.gmap, 0, 0, 3, 6)
		self.gmapLayout.addWidget(self.droneStatusLayout, 0, 5, 1, 1)
		self.gmapLayout.addWidget(self.textCommandLayout, 1, 4, 1, 2)
		self.gmapLayout.addWidget(self.logText, 2, 4, 1, 2)
		self.gmapLayout.addWidget(self.takeoffBtn, 2, 1, 1, 1)
		self.gmapLayout.addWidget(self.targetBtn, 2, 2, 1, 1)

		self.gmapLayout.setColumnStretch(0, 1)
		self.gmapLayout.setColumnStretch(1, 1)
		self.gmapLayout.setColumnStretch(2, 1)
		self.gmapLayout.setColumnStretch(3, 1)
		self.gmapLayout.setColumnStretch(4, 2)
		self.gmapLayout.setColumnStretch(5, 2)
		self.gmapLayout.setRowStretch(0, 6)
		self.gmapLayout.setRowStretch(1, 1)
		self.gmapLayout.setRowStretch(2, 2)
		

		# self.gmapLayout.setColumnStretch(0, 1)
		# self.gmapLayout.setColumnStretch(1, 1)
		# self.gmapLayout.setColumnStretch(2, 1)
		# self.gmapLayout.setColumnStretch(3, 1)
		# self.gmapLayout.setColumnStretch(4, 2)
		# self.gmapLayout.setRowStretch(0, 3)
		# self.gmapLayout.setRowStretch(1, 1)
		self.gmapWidget = QWidget()
		self.gmapWidget.setLayout(self.gmapLayout)
		self.stackedLayout.addWidget(self.gmapWidget)

		self.streaming = QWidget()
		self.streaming.setStyleSheet("""
			background-color:rgba(130, 100, 50, 50%);
			border-color: rgb(255,255,255);
			border: none;""")
		self.stackedLayout.addWidget(self.streaming)

		self.gridLayout = QGridLayout()
		self.gridLayout.addWidget(self.stackedLayout, 0, 0, 1, 2)
		self.gridLayout.addWidget(self.navBar, 0, 0, 1, 1)
		self.gridLayout.setColumnStretch(0, 1)
		self.gridLayout.setColumnStretch(1, 10)

		self.setLayout(self.gridLayout)
		self.resize(2280, 1520)

	def on_takeoff_clicked(self):
		self.server.send("1", "take off!")

	def on_map_clicked(self):
		print "clicked"
		self.stackedLayout.setCurrentIndex(0)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()


	def on_streaming_clicked(self):
		print "clicked"
		self.stackedLayout.setCurrentIndex(1)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()

	def on_textcommand_clicked(self):
		textCommand = self.textCommandLayout.commandText.toPlainText()
		if self.server.droneList[0]:
			self.server.send("1", textCommand)


	def gcs_server_init(self):
		self.logText.append("Connecting to the server...")
		self.server = GCSSeverThread("127.0.0.1", 43213)

		""" Server timer init """
		self.server_timer = QTimer(self)
		self.server_timer.timeout.connect(self.on_server_timer)
		self.server_timer.start(1000)

		self.server.start()

	def on_server_timer(self):
		try:
			serverReport = self.server.serverReportQueue.get_nowait()
			if serverReport.type == ServerReport.TEXT:
				self.logText.append(serverReport.data)

				
			elif serverReport.type == ServerReport.NEW:
				# self.logText.append(serverReport.data)
				self.droneStatusLayout.add(serverReport.data)
			elif serverReport.type == ServerReport.TERMINATE:
				self.gmap.frame.evaluateJavaScript('remove_marker(%s)' % serverReport.data)
				self.droneStatusLayout.remove(serverReport.data)

		except Queue.Empty as e:
			pass


		for drone in self.server.droneList:
			info = drone.drone.get_info()
			print info
			self.gmap.frame.evaluateJavaScript('update_marker(%s, %s, %s)' % (info['id'], info['location']['lat'], info['location']['lng']))






if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = QApplication(sys.argv)
	style = QSSHelper.open_qss('style.qss')
	app.setStyleSheet(style)
	frame = MainFrame()
	frame.show()
	# try:
	# 	while True:
	# 		time.sleep(.1)
	# except KeyboardInterrupt:
	# 	print "KeyboardInterrupt"
	# 	sys.exit(app.exec_())
	sys.exit(app.exec_())

	
