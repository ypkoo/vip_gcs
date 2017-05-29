from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from VipWidget import *
from GCSServer import *

import sys, os, time, signal, json, datetime
from aqua.qsshelper import QSSHelper

HOST = ""
PORT = 43212

def LOG(logger_, text):
	logger = "[ "+logger_+" ]"
	return "%s %s" % (logger, text)

class JSCommunicator(QObject):
	def __init__(self, signal):
		super(JSCommunicator, self).__init__()

		self.signal = signal

	@pyqtSlot(str)
	def emit_signal(self, msg):
		self.signal.emit(msg)


class GMapWebView(QWebView):

	def __init__(self, source, signal):
		super(GMapWebView, self).__init__()

		
		file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), source))
		local_url = QUrl.fromLocalFile(file_path)
		self.load(local_url)

		self.signal = signal
		self.jsCommunicator = JSCommunicator(self.signal)

		self.frame = self.page().mainFrame()
		self.frame.addToJavaScriptWindowObject('jsCommunicator', self.jsCommunicator)


class VipContext(object):

	def __init__(self):

		curLat = None
		curLng = None
		curAlt = None
		m600Lat = None
		m600Lng = None
		m600Alt = None

		self.isM600Connected = False

class MainFrame(QWidget):

	jsSignal = pyqtSignal(str)

	def __init__(self):
		super(MainFrame, self).__init__()

		self.frame_init()
		self.gcs_server_init()
		# jsSignal = pyqtSignal(str)
		self.jsSignal.connect(self.js_signal_handler)
		self.context = VipContext()
		
	
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
		self.gmap = GMapWebView("gmap-drone.html", self.jsSignal)

		fontDB = QFontDatabase()
		latoLight = fontDB.addApplicationFont("fonts/Lato/Lato-Light.ttf")
		if latoLight < 0:
			print "font load failed"
		latoLightFont = fontDB.font("fonts/Lato/Lato-Light.ttf", "normal", 12)
		# if not latoLight == -1:
		# 	print "font load successed"
		# 	fontDB = QFontDatabase()
		# 	self.fontStyles = fontDB.styles('LatoLight')
		# 	self.fontFamilies = QFontDatabase.applicationFontFamilies(latoLight)
		# 	for fontFamily in self.fontFamilies:
		# 		self.font = fontDB.font(fontFamily, self.fontStyles.first(), 24)

		self.logText = QTextEdit()
		self.logText.setReadOnly(True)
		# self.logText.setFont(latoLightFont)
		
		self.logText.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			padding: 10px;
			margin-right: 20px;
			margin-bottom: 10px;
			border-style: solid;
			border-color: white;
			border-radius: 20px;""")

		self.takeoffBtn = QPushButton("")
		self.takeoffBtn.setIcon(QIcon('image/takoff.png'))
		self.takeoffBtn.setIconSize(QSize(130,130))
		self.targetBtn = QPushButton("")
		self.targetBtn.setIcon(QIcon('image/target.png'))
		self.targetBtn.setIconSize(QSize(130,130))
		self.stopBtn = QPushButton("")
		self.stopBtn.setIcon(QIcon('image/target.png'))
		self.stopBtn.setIconSize(QSize(130,130))

		self.takeoffBtn.clicked.connect(self.on_takeoff_clicked)
		self.targetBtn.clicked.connect(self.on_target_clicked)
		self.stopBtn.clicked.connect(self.on_stop_clicked)

		# self.gmapLayout.addWidget(self.gmap, 0, 0, 2, 5)
		# self.gmapLayout.addWidget(self.logText, 1, 4, 1, 1)
		# self.gmapLayout.addWidget(self.takeoffBtn, 1, 1, 1, 1)
		# self.gmapLayout.addWidget(self.targetBtn, 1, 2, 1, 1)

		self.gmapLayout.addWidget(self.gmap, 0, 0, 3, 6)
		self.gmapLayout.addWidget(self.droneStatusLayout, 0, 5, 2, 1)
		# self.gmapLayout.addWidget(self.textCommandLayout, 1, 1, 1, 3)
		self.gmapLayout.addWidget(self.logText, 2, 4, 1, 2)
		""" Buttons
		self.gmapLayout.addWidget(self.takeoffBtn, 2, 1, 1, 1)
		self.gmapLayout.addWidget(self.targetBtn, 2, 2, 1, 1)
		self.gmapLayout.addWidget(self.stopBtn, 2, 3, 1, 1)
		"""

		self.gmapLayout.setColumnStretch(0, 1)
		self.gmapLayout.setColumnStretch(1, 1)
		self.gmapLayout.setColumnStretch(2, 1)
		self.gmapLayout.setColumnStretch(3, 1)
		self.gmapLayout.setColumnStretch(4, 2)
		self.gmapLayout.setColumnStretch(5, 1)
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
		self.gridLayout.addWidget(self.stackedLayout, 0, 0, 2, 2)
		self.gridLayout.addWidget(self.navBar, 0, 0, 1, 1)
		self.gridLayout.setColumnStretch(0, 1)
		self.gridLayout.setColumnStretch(1, 10)
		self.gmapLayout.setRowStretch(0, 1)
		self.gmapLayout.setRowStretch(1, 4)

		self.setLayout(self.gridLayout)
		self.resize(2280, 1520)

	def on_takeoff_clicked(self):
		if self.context.isM600Connected:
			command = {
				"type": "control",
				"data": {
					"command": "start",
					"lat": self.context.m600Lat,
					"lng": self.context.m600Lng,
					"alt": self.context.m600Alt,
					"timestamp": str(datetime.datetime.now()),
				}
			}
			self.server.send_to_all(json.dumps(command))

			self.logText.append(LOG("GUI", "Send start command to drones"))

	def on_target_clicked(self):
		if self.context.isM600Connected:
			command = {
				"type": "control",
				"data": {
					"command": "go",
					"lat": self.context.m600Lat,
					"lng": self.context.m600Lng,
					"alt": self.context.m600Alt,
					"timestamp": str(datetime.datetime.now()),
				}
			}
			self.server.send_to_all(json.dumps(command))

			self.logText.append(LOG("GUI", "Send go command to drones"))

	def on_stop_clicked(self):
		if self.context.isM600Connected:
			command = {
				"type": "control",
				"data": {
					"command": "stop",
					"lat": self.context.m600Lat,
					"lng": self.context.m600Lng,
					"alt": self.context.m600Alt,
					"timestamp": str(datetime.datetime.now()),
				}
			}
			self.server.send_to_all(json.dumps(command))

			self.logText.append(LOG("GUI", "Send stop command to drones"))

	def on_map_clicked(self):
		self.stackedLayout.setCurrentIndex(0)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()


	def on_streaming_clicked(self):
		self.stackedLayout.setCurrentIndex(1)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()

	def on_textcommand_clicked(self):
		textCommand = str(self.textCommandLayout.commandText.toPlainText())
		command = {
				"type": "textcommand",
				"data": textCommand,
			}
		self.server.send("1", json.dumps(command))
		text = "Send text command %s to drone 1" % textCommand
		self.logText.append(text)


	def gcs_server_init(self):
		self.logText.append(LOG("GCS", "Connecting to the server..."))
		self.server = GCSSeverThread(HOST, PORT)

		""" Server timer init """
		self.server_timer = QTimer(self)
		self.server_timer.timeout.connect(self.on_server_timer)
		self.server_timer.start(1000)

		self.server.start()

	def js_signal_handler(self, msg_):


		msg = str(msg_).split()
		print msg

		if msg[0] == "marker_click_event":
			self.context.lat = msg[1]
			self.context.lng = msg[2]
			text = "(%s, %s) clicked." % (self.context.lat[:-5], self.context.lng[:-5])
			self.logText.append(LOG("GUI", text))


		elif msg[0] == "map_click_event":
			self.context.lat = msg[1]
			self.context.lng = msg[2]
			text = "(%s, %s) clicked." % (self.context.lat[:-10], self.context.lng[:-10])
			self.logText.append(LOG("GUI", text))



	def on_server_timer(self):
		try:
			serverReport = self.server.serverReportQueue.get_nowait()
			if serverReport.type == ServerReport.TEXT:
				self.logText.append(LOG("Server", serverReport.data))

				
			elif serverReport.type == ServerReport.NEW:
				self.logText.append(LOG("Server", 'A new drone %s is connected.' % serverReport.data))
				if serverReport.data == "1":
					self.context.isM600Connected = True
				self.droneStatusLayout.add(serverReport.data)
			elif serverReport.type == ServerReport.TERMINATE:
				self.gmap.frame.evaluateJavaScript('remove_marker(%s)' % serverReport.data)
				self.droneStatusLayout.remove(serverReport.data)
				self.logText.append(LOG("Server", 'Drone %s connection closed.' % serverReport.data))
			elif serverReport.type == ServerReport.ALEXA:
				self.logText.append(LOG("Alexa", serverReport.data))

		except Queue.Empty as e:
			pass


		for drone in self.server.droneList:
			info = drone.drone.get_info()
			# print info

			if info['id'] == "1":
				self.context.m600Lat = info['location']['lat']
				self.context.m600Lng = info['location']['lng']
				self.context.m600Alt = info['location']['alt']

			self.droneStatusLayout.setStatus(info)
			self.gmap.frame.evaluateJavaScript('update_marker(%s, %s, %s)' % (info['id'], info['location']['lat'], info['location']['lng']))






if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = QApplication(sys.argv)
	QFontDatabase.addApplicationFont("/home/ypkoo/VIP_GCS/fonts/Lato/Lato-Light.ttf")
	QFontDatabase.addApplicationFont("/home/ypkoo/VIP_GCS/fonts/Lato/Lato-Bold.ttf")
	QFontDatabase.addApplicationFont("/home/ypkoo/VIP_GCS/fonts/Open_Sans/OpenSans-Light.ttf")
	# latoLight = QFontDatabase.addApplicationFont("fonts/Lato/Lato-Light.ttf")
	# if not latoLight == -1:
	# 	print "font load successed"
	# 	fontDB = QtGui.QFontDatabase()
	# 	self.fontStyles = fontDB.styles('LatoLight')
	# 	self.fontFamilies = QFontDatabase.applicationFontFamilies(latoLight)
	# 	for fontFamily in self.fontFamilies:
	# 		self.font = fontDB.font(fontFamily, self.fontStyles.first(), 24)

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

	
