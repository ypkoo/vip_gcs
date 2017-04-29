from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebView, QWebPage
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

import sys, os


class GMapWebView(QWebView):

	def __init__(self):
		super(GMapWebView, self).__init__()
		file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "gmap-drone.html"))
		local_url = QUrl.fromLocalFile(file_path)
		self.load(local_url)

		self.frame = self.page().mainFrame()




class MainFrame(QMainWindow):


	def __init__(self):
		super(MainFrame, self).__init__()

		self.gmap = GMapWebView()
		self.grid = QGridLayout()
		self.grid.addWidget(self.gmap, 0, 0)

		main_frame = QWidget()
		main_frame.setLayout(self.grid)

		self.setCentralWidget(main_frame)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	frame = MainFrame()
	frame.show()
	sys.exit(app.exec_())