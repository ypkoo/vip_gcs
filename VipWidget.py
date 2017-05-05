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