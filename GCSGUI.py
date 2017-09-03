from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
from VipWidget import *
from GCSServer import *

import sys, os, time, signal, json, datetime
from aqua.qsshelper import QSSHelper

HOST = ""
PORT = 43211

""" test """

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

		curSelected = None

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

		self.droneStatusLayout.addWidget("0")
		self.droneStatusLayout.clicked_connect("0", self.on_dronestatus_clicked)


		self.streamingBtn.clicked.connect(self.on_streaming_clicked)
		self.mapBtn.clicked.connect(self.on_map_clicked)

		
		self.gmapLayout = QGridLayout()
		self.gmap = GMapWebView("gmap-drone.html", self.jsSignal)


		self.logText = QTextEdit()
		self.logText.setReadOnly(True)
		
		self.logText.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			padding: 10px;
			margin-right: 20px;
			margin-bottom: 10px;
			border-style: solid;
			border-color: white;
			border-radius: 20px;""")



		""" Command layout """
		self.cmdWidget = QWidget()
		# self.cmdWidget.hide()
		self.cmdWidget.setStyleSheet("background-color:rgba(0, 0, 0, 0%);")
		self.cmdLayout = QGridLayout()
		# self.cmdLayout.setSpacing(0)
		self.cmdLayout.setContentsMargins(0,0,0,0)
		self.cmdLayout.setAlignment(Qt.AlignTop)
		self.cmdWidget.setLayout(self.cmdLayout)
		


		self.startBtn = VipCommandBtn("Start")
		self.goBtn = VipCommandBtn("Go")
		self.streamingOnBtn = VipCommandBtn("StreamOn")
		# self.streamingOffBtn = VipCommandBtn("StreamOff")
		self.streamingOffBtn = VipCommandBtn("Redetect")		
		self.trackingOnBtn = VipCommandBtn("TrackingOn")
		self.trackingOffBtn = VipCommandBtn("TrackingOff")
		self.redetectBtn = VipCommandBtn("Redetect")
		self.zoomInBtn = VipCommandBtn("ZoomIn")
		self.zoomOutBtn = VipCommandBtn("ZoomOut")
		self.stopBtn = VipCommandBtn("Stop")

		self.droneInfo = QWidget()
		self.droneInfo.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			margin-left: 10px;
			margin-bottom: 10px;
			border: 1px solid white;
			border-radius: 20px;""")
		self.droneInfoLayout = QGridLayout()
		self.droneInfo.setLayout(self.droneInfoLayout)
		self.textCommand = QTextEdit()
		self.textCommandBtn = QPushButton("send")
		self.curDroneLabel = QLabel()
		self.droneInfoLayout.addWidget(self.curDroneLabel, 0, 0)
		self.droneInfoLayout.addWidget(self.textCommand, 1, 0)
		self.droneInfoLayout.addWidget(self.textCommandBtn, 1, 1)
		self.textCommandBtn.clicked.connect(self.on_textcommandbtn_clicked)

		

		# self.cmdLayout.addWidget(self.droneIDLabel, 0, 0, 1, 1)
		# self.cmdLayout.addWidget(self.startBtn, 0, 0, 1, 1)
		# self.cmdLayout.addWidget(self.goBtn, 1, 0, 1, 1)
		# self.cmdLayout.addWidget(self.streamingOnBtn, 0, 1, 1, 1)
		# self.cmdLayout.addWidget(self.streamingOffBtn, 1, 1, 1, 1)
		# self.cmdLayout.addWidget(self.trackingOnBtn, 0, 2, 1, 1)
		# self.cmdLayout.addWidget(self.trackingOffBtn, 1, 2, 1, 1)
		# self.cmdLayout.addWidget(self.zoomInBtn, 0, 3, 1, 1)
		# self.cmdLayout.addWidget(self.zoomOutBtn, 1, 3, 1, 1)
		# self.cmdLayout.addWidget(self.redetectBtn, 0, 4, 1, 1)
		# self.cmdLayout.addWidget(self.stopBtn, 1, 4, 1, 1)

		self.cmdLayout.addWidget(self.startBtn, 0, 0, 1, 1)
		self.cmdLayout.addWidget(self.goBtn, 1, 0, 1, 1)
		self.cmdLayout.addWidget(self.streamingOnBtn, 2, 0, 1, 1)
		self.cmdLayout.addWidget(self.streamingOffBtn, 3, 0, 1, 1)
		self.cmdLayout.addWidget(self.trackingOnBtn, 4, 0, 1, 1)
		self.cmdLayout.addWidget(self.trackingOffBtn, 5, 0, 1, 1)
		self.cmdLayout.addWidget(self.zoomInBtn, 6, 0, 1, 1)
		self.cmdLayout.addWidget(self.zoomOutBtn, 7, 0, 1, 1)
		self.cmdLayout.addWidget(self.redetectBtn, 8, 0, 1, 1)
		self.cmdLayout.addWidget(self.stopBtn, 9, 0, 1, 1)


		self.startBtn.clicked.connect(self.on_startbtn_clicked)
		self.goBtn.clicked.connect(self.on_gobtn_clicked)
		self.streamingOnBtn.clicked.connect(self.on_streamingonbtn_clicked)
		self.streamingOffBtn.clicked.connect(self.on_streamingoffbtn_clicked)
		self.trackingOnBtn.clicked.connect(self.on_trackingonbtn_clicked)
		self.trackingOffBtn.clicked.connect(self.on_trackingoffbtn_clicked)
		self.zoomInBtn.clicked.connect(self.on_zoominbtn_clicked)
		self.zoomOutBtn.clicked.connect(self.on_zoomoutbtn_clicked)
		self.redetectBtn.clicked.connect(self.on_redetectbtn_clicked)
		self.stopBtn.clicked.connect(self.on_stopbtn_clicked)

		# self.cmdLayout.setRowStretch(0, 2)
		# self.cmdLayout.setRowStretch(1, 10)
		# self.cmdLayout.setColumnStretch(0, 2)
		# self.cmdLayout.setColumnStretch(1, 2)
		# self.cmdLayout.setColumnStretch(2, 2)
		# self.cmdLayout.setColumnStretch(3, 2)
		# self.cmdLayout.setColumnStretch(4, 2)


		self.sendtoallBox = QCheckBox("send to all")

		# self.gmapLayout.addWidget(self.sendtoallBox, 1, 0, 1, 1)
		self.gmapLayout.addWidget(self.gmap, 0, 0, 3, 6)
		self.gmapLayout.addWidget(self.droneStatusLayout, 0, 5, 2, 1)
		# self.gmapLayout.addWidget(self.textCommandLayout, 1, 1, 1, 3)
		self.gmapLayout.addWidget(self.cmdWidget, 0, 0, 3, 1)
		self.gmapLayout.addWidget(self.logText, 2, 4, 1, 2)


		self.gmapLayout.setColumnStretch(0, 1)
		self.gmapLayout.setColumnStretch(1, 2)
		self.gmapLayout.setColumnStretch(2, 2)
		self.gmapLayout.setColumnStretch(3, 2)
		self.gmapLayout.setColumnStretch(4, 2)
		self.gmapLayout.setColumnStretch(5, 2)
		self.gmapLayout.setRowStretch(0, 6)
		self.gmapLayout.setRowStretch(1, 1)
		self.gmapLayout.setRowStretch(2, 1)
		

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
		# self.gridLayout.addWidget(self.navBar, 0, 0, 1, 1)
		self.gridLayout.setColumnStretch(0, 1)
		self.gridLayout.setColumnStretch(1, 10)
		self.gmapLayout.setRowStretch(0, 1)
		self.gmapLayout.setRowStretch(1, 4)

		self.setLayout(self.gridLayout)
		self.resize(2280, 1520)

	def on_startbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "start",
		}
		
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send start command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send start command to drone %s" % self.context.curSelected))

	def on_gobtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "go",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send go command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send go command to drone %s" % self.context.curSelected))

	def on_streamingonbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "stream on",
		}

		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send streaming on command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send streaming on command to drone %s" % self.context.curSelected))

	def on_streamingoffbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "stream off"
			# "command": "stream off", # kdw
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send streaming off command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send streaming off command to drone %s" % self.context.curSelected))

	def on_trackingonbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "tracking on",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send tracking on command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send tracking on command to drone %s" % self.context.curSelected))

	def on_trackingoffbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "tracking off",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send tracking off command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send tracking off command to drone %s" % self.context.curSelected))

	def on_zoominbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "zoom in",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send zoom in command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send zoom in command to drone %s" % self.context.curSelected))

	def on_zoomoutbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "zoom out",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send zoom out command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send zoom out command to drone %s" % self.context.curSelected))

	def on_redetectbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "redetect",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send redetect command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send redetect command to drone %s" % self.context.curSelected))

	def on_stopbtn_clicked(self):
		command = {
			"topic": "gcs",
			"command": "stop",
		}
		if self.context.curSelected == "0":
			self.server.send_to_all(json.dumps(command))
			self.logText.append(LOG("GUI", "Send stop command to all drones"))
		else:
			self.server.send(self.context.curSelected, json.dumps(command))
			self.logText.append(LOG("GUI", "Send stop command to drone %s" % self.context.curSelected))

	def on_map_clicked(self):
		self.stackedLayout.setCurrentIndex(0)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()


	def on_streaming_clicked(self):
		self.stackedLayout.setCurrentIndex(1)
		self.mapBtn.raise_()
		self.streamingBtn.raise_()

	def on_textcommandbtn_clicked(self):
		textCommand = str(self.textCommand.toPlainText())
		command = {
				"type": "dronemanager",
				"data": {
							"command": "textcommand",
							"contents": textCommand, 
						}
			}
		self.server.send(self.context.curSelected, json.dumps(command))
		text = "Send text command %s to drone %s" % (textCommand, self.context.curSelected)
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

	def on_dronestatus_clicked(self, id_):
		self.context.curSelected = id_




	def on_server_timer(self):
		try:
			serverReport = self.server.serverReportQueue.get_nowait()
			if serverReport.type == ServerReport.TEXT:
				self.logText.append(LOG("Server", serverReport.data))

				
			elif serverReport.type == ServerReport.NEW:
				self.logText.append(LOG("Server", 'A new drone %s is connected.' % serverReport.data))
				# if serverReport.data == "1":
				# 	self.context.isM600Connected = True
				self.droneStatusLayout.addWidget(serverReport.data)
				self.droneStatusLayout.clicked_connect(serverReport.data, self.on_dronestatus_clicked)
			elif serverReport.type == ServerReport.TERMINATE:
				self.gmap.frame.evaluateJavaScript('remove_marker(%s)' % serverReport.data)
				self.droneStatusLayout.removeWidget(serverReport.data)
				self.logText.append(LOG("Server", 'Drone %s connection closed.' % serverReport.data))
			elif serverReport.type == ServerReport.ALEXA:
				self.logText.append(LOG("Alexa", serverReport.data))

		except Queue.Empty as e:
			pass


		for drone in self.server.droneList:
			info = drone.drone.get_info()


			self.droneStatusLayout.setStatus(info)
			self.gmap.frame.evaluateJavaScript('update_marker(%s, %s, %s)' % (info['id'], info['location']['lat'], info['location']['lng']))






if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	app = QApplication(sys.argv)
	QFontDatabase.addApplicationFont("/home/ypkoo/VIP_GCS/fonts/Lato/Lato-Light.ttf")
	QFontDatabase.addApplicationFont("/home/ypkoo/VIP_GCS/fonts/Lato/Lato-Bold.ttf")
	QFontDatabase.addApplicationFont("/home/ypkoo/VIP_GCS/fonts/Open_Sans/OpenSans-Light.ttf")


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
	app.quit()


	
