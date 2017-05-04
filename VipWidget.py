from PyQt4.QtGui import *
from PyQt4.QtCore import *


class VipNavBarBtn(QPushButton):
	def __init__(self, default_icon, hover_icon):
		super(VipNavBarBtn, self).__init__()

		self.default_icon = default_icon
		self.hover_icon = hover_icon

		self.setIcon(self.default_icon)

		self.setMouseTracking(True)

		self.setStyleSheet("""
			background-color: rgba(0, 0, 0, 0%)""")

	def enterEvent(self,event):
		print("Enter")
		self.setIcon(self.hover_icon)
		# self.setStyleSheet("""
		# 	background-color:#45b545;
		# 	border-bottom: 5px solid rgb(255,255,255);""")

	def leaveEvent(self,event):
		# self.setStyleSheet("background-color:yellow;")
		print("Leave")
		self.setIcon(self.default_icon)