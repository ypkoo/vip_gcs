from PyQt4.QtGui import *
from PyQt4.QtCore import *

class VipNavBar(QWidget):
	def __init__(self):
		super(VipNavBar, self).__init__()

		self._btnList = []

		self._layout = QVBoxLayout()

		""" remove margin and padding """
		self._layout.setSpacing(0)
		self._layout.setContentsMargins(0,0,0,0)

		self._layout.setAlignment(Qt.AlignTop)
		self.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			padding-top: 20px;
			margin: 0px;""")


		self.setLayout(self._layout)
		self.setMouseTracking(True)


	""" TODO: add declaration of VipNavBarBtn here """
	def add_btn(self, btn):
		self._btnList.append(btn)
		self._layout.addWidget(btn)


	def enterEvent(self,event):
		for btn in self._btnList:
			btn.setIcon(btn.icon_others_hover)

	def leaveEvent(self,event):
		# self.setStyleSheet("background-color:yellow;")
		for btn in self._btnList:
			btn.setIcon(btn.icon_default)


class VipNavBarBtn(QPushButton):
	def __init__(self, *args, **kwargs):
		super(VipNavBarBtn, self).__init__()

		
		self.icon_default = kwargs.pop('icon_default')
		self.icon_hover = kwargs.pop('icon_hover')
		self.icon_others_hover = kwargs.pop('icon_others_hover')


		self.setIcon(self.icon_default)
		self._size = kwargs.pop('icon_size', 110)
		self.setIconSize(QSize(self._size, self._size))

		self.setMouseTracking(True)

		self.setStyleSheet("""
			background-color: rgba(0, 0, 0, 50%)""")

	def enterEvent(self,event):
		self.setIcon(self.icon_hover)
		# self.setStyleSheet("""
		# 	background-color:#45b545;
		# 	border-bottom: 5px solid rgb(255,255,255);""")

	def leaveEvent(self,event):
		# self.setStyleSheet("background-color:yellow;")
		self.setIcon(self.icon_others_hover)
		pass

class VipStatusLayout(QWidget):
	def __init__(self):
		super(VipStatusLayout, self).__init__()

		self._droneStatusList = []

		self._layout = QVBoxLayout()

		""" remove margin and padding """
		self._layout.setSpacing(0)
		# self._layout.setContentsMargins(10,10,10,10)

		self._layout.setAlignment(Qt.AlignTop)
		self.setStyleSheet("""
			background-color:rgba(0, 0, 0, 100%);
			padding-top: 20px;
			margin: 10px;""")


		self.setLayout(self._layout)
		# self.setMouseTracking(True)

		# self.sendtoall = VipSendToAll(0)
		# self._droneStatusList.append(self.sendtoall)
		# self._layout.addWidget(self.sendtoall)

		# self.sendtoall = VipDroneStatus("0")
		# self._droneStatusList.append(self.sendtoall)
		# self._layout.addWidget(self.sendtoall)

	def addWidget(self, id_):
		# self._btnList.append(btn)

		status = VipDroneStatus(id_)
		self._droneStatusList.append(status)

		""" Insert a widget in order """
		if self._layout.count() > 0:
			for i in range(self._layout.count()):
				if int(id_) < int(self._layout.itemAt(i).widget().id):
					self._layout.insertWidget(i, status)
					break
				if i == self._layout.count() - 1:
					self._layout.addWidget(status)
		else:
			self._layout.addWidget(status)


		
	def removeWidget(self, id_):
		for droneStatus in self._droneStatusList:
			if droneStatus.id == id_:
				toRemove = droneStatus
				break

		self._layout.removeWidget(toRemove)
		toRemove.deleteLater()
		self._droneStatusList.remove(toRemove)
		toRemove = None

	"""
		status:
	"""
	def setStatus(self, info):

		target = self._drone_by_id(info['id'])
		target.setStatus(info)

	def clicked_connect(self, id_, targetFunc):
		target = self._drone_by_id(id_)
		QObject.connect(target, SIGNAL("droneStatusClicked"), targetFunc)

	def _drone_by_id(self, id_):
		for droneStatus in self._droneStatusList:
			if droneStatus.id == id_:
				return droneStatus

# class VipSendToAll(QWidget):
# 	def __init__(self, id_):
# 		super(VipSendToAll, self).__init__()

# 		self.id = id_
# 		self._layout = QGridLayout()
# 		self.statusText = QLabel("Send to all")
# 		self.setLayout(self._layout)
# 		self._layout.addWidget(self.statusText, 0, 0)

# 		self.setStyleSheet("""
# 			background-color: rgba(0, 0, 0, 50%);
# 			border-radius: 20px;
# 			border: 3px solid green;
# 			color: yellow;
# 			height: 30px;""")

# 	def enterEvent(self,event):
# 		self.setCursor(QCursor(Qt.PointingHandCursor))

# 	def mouseReleaseEvent(self, event):
# 		self.emit(SIGNAL("droneStatusClicked"), self.id)

class VipDroneStatus(QWidget):
	def __init__(self, id_):
		super(VipDroneStatus, self).__init__()

		self._layout = QGridLayout()

		if id_ == "0":
			self.statusText = QLabel("Send to all")
		else:
			self.statusText = QLabel("Drone %s\n\n\n" % (id_))
		# self.statusText.setReadOnly(True)
		self.setLayout(self._layout)
		self._layout.addWidget(self.statusText, 0, 0)
		


		self.id = id_

		if self.id == "0":
			self.setStyleSheet("""
				background-color: rgba(0, 0, 0, 50%);
				border-radius: 20px;
				border: 3px solid green;
				color: yellow;
				""")
		else:
			self.setStyleSheet("""
				background-color: rgba(0, 0, 0, 50%);
				border-radius: 20px;
				border: 3px solid red;
				color: yellow;
				""")


	def setStatus(self, info):
		# self.setProperty('border-color', 'green')
		# self.setProperty('color', QColor(0, 0, 255, 127))
		if info['activate'] == 'on':
			self.setStyleSheet("""
				background-color: rgba(0, 0, 0, 50%);
				border-radius: 20px;
				border: 3px solid green;
				color: yellow;
				""")
		text = """Drone %s
		
lat: %s
lng: %s
alt: %s
yaw: %s
battery: %s%%
""" % (info['id'], info['location']['lat'], info['location']['lng'], info['location']['alt'], info['yaw'], info['battery'])
		
		# text = "Drone %s" % info['id']
		self.statusText.setText(text)
	
	def enterEvent(self,event):
		self.setCursor(QCursor(Qt.PointingHandCursor))

	def mouseReleaseEvent(self, event):
		self.emit(SIGNAL("droneStatusClicked"), self.id)




class VipTextCommandLayout(QWidget):
	def __init__(self):
		super(VipTextCommandLayout, self).__init__()

		# self._btnList = []

		self._layout = QHBoxLayout()
		self.commandText = QTextEdit()
		self.commandBtn = QPushButton("send")

		self.commandText.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			padding-top: 20px;
			margin: 10px;""")
		self.commandBtn.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			padding-top: 20px;
			margin: 10px;""")

		self._layout.addWidget(self.commandText)
		self._layout.addWidget(self.commandBtn)

		""" remove margin and padding """
		self._layout.setSpacing(0)
		# self._layout.setContentsMargins(10,10,10,10)

		# self._layout.setAlignment(Qt.AlignCenter)
		self.setStyleSheet("""
			background-color:rgba(0, 0, 0, 100%);
			padding-top: 20px;
			margin: 0px;""")


		self.setLayout(self._layout)
		# self.setMouseTracking(True)

	def add(self, btn):
		# self._btnList.append(btn)
		btn.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			color: white;
			padding-top: 20px;
			margin: 10px;""")
		self._layout.addWidget(btn)


class VipCommandLayout(QWidget):
	def __init__(self):
		super(VipCommandLayout, self).__init__()

		self._layout = QGridLayout()
		self.setLayout(self._layout)

class VipCommandBtn(QPushButton):
	def __init__(self, *args, **kwargs):
		super(VipCommandBtn, self).__init__(*args, **kwargs)

		self.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			border: 1px solid white;
			margin-bottom: 10px;
			margin-top: 0px;
			color: white;
			height: 70px;
			width: 50px;""")

		self.setMouseTracking(True)

	def enterEvent(self,event):
		self.setCursor(QCursor(Qt.PointingHandCursor))
		self.setStyleSheet("""
			background-color:rgba(244, 208, 63, 90%);
			border: 1px solid white;
			margin-bottom: 10px;
			margin-top: 0px;
			color: white;
			height: 70px;
			width: 50px;""")

	def leaveEvent(self,event):
		self.setStyleSheet("""
			background-color:rgba(0, 0, 0, 50%);
			border: 1px solid white;
			margin-bottom: 10px;
			margin-top: 0px;
			color: white;
			height: 70px;
			width: 50px;""")