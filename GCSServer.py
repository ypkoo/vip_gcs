"""
GCS Server for VIP project

Yoonpyo Koo (ypkoo@lanada.kaist.ac.kr)

Reference
Eli Bendersky's code sample (http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python/)
Pollable Queue http://chimera.labs.oreilly.com/books/1230000000393/ch12.html
"""

import socket, struct, threading, Queue, select, json, sys

class Command(object):
	"""
	A command to a client thread. 
	"""
	SEND, GET_INFO, CLOSE = range(3)

	def __init__(self, type, data=None):
		self.type = type
		self.data = data

class Reply(object):
	"""
	A reply from a client thread. Each type has its associated data:

	ERROR:
		The error string
	SUCCESS:
		The received message
	"""
	ERROR, SUCCESS = range(2)

	def __init__(self, type, data=None):
		self.type = type
		self.data = data

class ServerReport(object):

	NEW, TEXT = range(2)

	def __init__(self, type_, data=None):
		self.type = type_
		self.data = data


class Drone(object):

	def __init__(self, id_):

		self.id = id_

		""" Location Info """
		self.lat = None
		self.lng = None
		self.alt = None

		""" Status Flags """
		self.isFlying = None
		self.isTracking = None
		self.isLocating = None

		self.lastUpdate = None

		""" TO DO: reimplement using a queue """
		self.reportQueue = None 

	def get_info(self):
		info = {
			'id': self.id,
			'location': (self.lat, self.lng, self.alt),
			'isFlying': self.isFlying,
			'isTracking': self.isTracking,
			'isLocating': self.isLocating,
			'lastUpdate': self.lastUpdate,
		}

		return info


class DroneClientThread(threading.Thread):

	def __init__(self, connection, id_, q):
		super(DroneClientThread, self).__init__()
		self.socket = connection
		self.q = q
		self.drone = Drone(id_)

		self.alive = threading.Event()
		self.alive.set()

		self._isIdSet = False


	def run(self):
		while self.alive.isSet():
			raw_data = self.socket.recv(2048)
			if raw_data:
				data = json.loads(raw_data)
				self._update_drone(data)

	def _update_drone(self, data):
		if data["type"] == "status":
			self.drone.lat = data["lat"]
			self.drone.lng = data["lng"]
			self.drone.alt = data["alt"]
			self.drone.lastUpdate = data["lastUpdate"]
		if data["type"] == "reply":
			self.drone.reply = data["reply"]
	

	def send(self, msg):
		self.socket.send(msg)




class GCSSeverThread(threading.Thread):
	"""
	GCS server thread. A GUI can communicate with a client thread
	by queuing and dequeuing queues in droneClientList.

	Sending a msg to a client:
		droneClientList[id].cmd_q.put(msg)
	Receiving a msg from a client:
		droneClientList[id].reply_q.get()
	"""


	def __init__(self, host, port):
		super(GCSSeverThread, self).__init__()
		self.droneList = []
		self.serverReportQueue = Queue.Queue()
		self.clientReportQueue = Queue.Queue()

		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.bind((host, port))
			self.socket.listen(5)
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, "Server is initiated successfully."))

		except socket.error, msg:
			text = "Couldnt connect with the socket-server: %s\n terminating server" % msg
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
			sys.exit(1)

	def run(self):
		while True:
			connection, address = self.socket.accept()
			print "connection", connection
			init_data = json.loads(connection.recv(2048))
			id_ = str(init_data["id"])
			text = 'A new drone %s is connected.' % id_
			print text
			# report = 
			self.serverReportQueue.put(ServerReport(ServerReport.NEW, text))

			self._create_client(connection, id_, self.clientReportQueue)


	def _create_client(self, connection, id_, q):
		client = DroneClientThread(connection, id_, q)
		self.droneList.append(client)

		client.start()

	def send(self, id_, msg):
		for drone in self.droneList:
			if drone.drone.id == id_:
				drone.send(msg)



if __name__ == "__main__":
	server = GCSSeverThread("127.0.0.1", 41234)
	server.start()
