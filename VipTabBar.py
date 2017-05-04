from PyQt4.QtGui import *
from PyQt4.QtCore import *


class VipTabBarWidget(QTabBar):
	def __init__(self, parent=None, *args, **kwargs):
		self.tabSize = QSize(kwargs.pop('width',100), kwargs.pop('height',25))
		QTabBar.__init__(self, parent, *args, **kwargs)
		self.setMouseTracking(True)


				 

	def enterEvent(self,event):
		print("Enter")
		self.setStyleSheet("""
			QTabBar::tab
			{
			  border: none;

			  color: rgb(220,220,220);

			}""")



		self.setTabIcon(0, QIcon('image/navi_hover_rotated.png'))
		self.setTabIcon(1, QIcon('image/video_hover_rotated.png'))
		print self.count()


	def leaveEvent(self,event):
		print("Leave")
		self.setStyleSheet("""
			QTabBar::tab
			{

			  border: none;

			  color: rgb(220,220,220);

			}""")
		
		self.setTabIcon(0, QIcon('image/navi_white_rotated.png'))
		self.setTabIcon(1, QIcon('image/video_white_rotated.png'))

	# def tabSizeHint(self, index):
	# 	if index == self.count() - 1:
	# 		size = QSize(0, 0)
	# 		for i in range(self.count() - 1):
	# 			size += QTabBar.tabSizeHint(self, i)
	# 		return QSize(self.width() - size.width(), size.height())
	# 	else:
	# 		return QTabBar.tabSizeHint(self, index)
