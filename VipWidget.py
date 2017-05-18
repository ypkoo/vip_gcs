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

	def add(self, id_):
		# self._btnList.append(btn)
		status = VipDroneStatus(id_)
		self._droneStatusList.append(status)
		self._layout.addWidget(status)

	def remove(self, id_):
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
		for droneStatus in self._droneStatusList:
			if droneStatus.id == info['id']:
				target = droneStatus
				print "find!"
				break

		target.setStatus(info)



class VipDroneStatus(QWidget):
	def __init__(self, id_):
		super(VipDroneStatus, self).__init__()

		self._layout = QGridLayout()

		self.statusText = QLabel("Drone %s\n\n\n" % (id_))
		# self.statusText.setReadOnly(True)
		self.setLayout(self._layout)
		self._layout.addWidget(self.statusText, 0, 0)
		


		self.id = id_
		# self.setText("Drone %s\n\n\n" % self.id)
		self.setStyleSheet("""
			background-color: rgba(0, 0, 0, 50%);
			border-radius: 20px;
			color: yellow;""")

	def setStatus(self, info):
		text = """Drone %s
		
lat: %s
lng: %s
alt: %s
""" % (info['id'], info['location']['lat'], info['location']['lng'], info['location']['alt'])

		self.statusText.setText(text)
		




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