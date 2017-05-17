"""
GCS Server for VIP project

Yoonpyo Koo (ypkoo@lanada.kaist.ac.kr)

Reference
Eli Bendersky's code sample (http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python/)
Pollable Queue http://chimera.labs.oreilly.com/books/1230000000393/ch12.html
"""

import socket, struct, threading, Queue, select, json, sys


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

class ClientReport(object):

	NEW, TERMINATE = range(2)

	def __init__(self, type_, data=None):
		self.type = type_
		self.data = data

class ServerReport(object):

	NEW, TEXT, TERMINATE = range(3)

	def __init__(self, type_, data=None):
		self.type = type_
		self.data = data

class PollableQueue(Queue.Queue, object):
	def __init__(self):
		# super(PollableQueue, self).__init__()
		super(PollableQueue, self).__init__()

		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind(('127.0.0.1', 0))
		server.listen(1)
		self._putsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._putsocket.connect(server.getsockname())
		self._getsocket, _ = server.accept()
		server.close()

	def fileno(self):
		return self._getsocket.fileno()

	def put(self, item):
		super(PollableQueue, self).put(item)
		# Queue.Queue.put(item)
		self._putsocket.send(b'x')

	def get(self):
		self._getsocket.recv(1)
		return super(PollableQueue, self).get()


class Drone(object):

	def __init__(self, id_=None):

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
			'location': {'lat': self.lat, 'lng': self.lng, 'alt': self.alt},
			'isFlying': self.isFlying,
			'isTracking': self.isTracking,
			'isLocating': self.isLocating,
			'lastUpdate': self.lastUpdate,
		}

		return info


class DroneClientThread(threading.Thread):

	def __init__(self, connection, q):
		super(DroneClientThread, self).__init__()
		self._socket = connection
		self._q = q
		self.drone = None
		self.isM600 = None

		self.alive = threading.Event()
		self.alive.set()

		# self._isIdSet = False


	def run(self):
		while self.alive.isSet():
			raw_data = self._socket.recv(2048)
			if raw_data:
				data = json.loads(raw_data)
				if self.drone:
					
					self._update_drone(data)
				else:
					if data["data"]["id"] == "1":
						self.isM600 = True
					else:
						self.isM600 = False
						
					self.drone = Drone(data["data"]["id"])
					self._update_drone(data)

					# self._q.put(ClientReport(ClientReport.NEW, data["data"]["id"]))
					self._q.put(ClientReport(ClientReport.NEW, self))
			else:
				print "socket closed"
				self.alive.clear()

		""" Terminate the thread """
		self._terminate_thread()

	def _update_drone(self, data):
		if data["type"] == "status":
			self.drone.lat = data["data"]["lat"]
			self.drone.lng = data["data"]["lng"]
			self.drone.alt = data["data"]["alt"]
			self.drone.lastUpdate = data["data"]["lastUpdate"]
		if data["type"] == "reply":
			self.drone.reply = data["reply"]

	def _terminate_thread(self):
		self._q.put(ClientReport(ClientReport.TERMINATE, self))
	
	def join(self, timeout=None):
		self.alive.clear()
		threading.Thread.join(self, timeout)

	def send(self, msg):
		self._socket.send(msg)




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
		self.pollingList = []
		self.serverReportQueue = Queue.Queue()

		""" Use custom Pollable queue to use select both for sockets and queues """
		self.clientReportQueue = PollableQueue()
		self.pollingList.append(self.clientReportQueue)

		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.bind((host, port))
			self.socket.listen(5)
			self.pollingList.append(self.socket)
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, "Server is initiated successfully."))

		except socket.error, msg:
			text = "Couldn't connect with the socket-server: %s\n terminating server" % msg
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
			sys.exit(1)

	def run(self):
		while True:
			readable, writable, exceptional = select.select(self.pollingList, [], [])
			for s in readable:

				if s is self.socket:
					""" New client """
					connection, address = self.socket.accept()
					print "connection", connection

					self._create_client(connection, self.clientReportQueue)
			
				else:
					""" Message from a client """
					msg = s.get()
					print msg

					if msg.type == ClientReport.NEW:
						""" TODO: what if id already exists? """
						self.droneList.append(msg.data)
						text = 'A new drone %s is connected.' % msg.data.drone.id
						self.serverReportQueue.put(ServerReport(ServerReport.NEW, msg.data.drone.id))
						self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
					elif msg.type == ClientReport.TERMINATE:
						text = 'Drone %s connection closed.' % msg.data.drone.id
						self.droneList.remove(msg.data)
						msg.data.join()
						self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
						self.serverReportQueue.put(ServerReport(ServerReport.TERMINATE, msg.data.drone.id))


	def _create_client(self, connection, q):
		client = DroneClientThread(connection, q)
		# self.droneList.append(client)

		client.start()

	def send(self, id_, msg):
		for drone in self.droneList:
			if drone.drone.id == id_:
				drone.send(msg)



if __name__ == "__main__":
	server = GCSSeverThread("127.0.0.1", 41234)
	server.start()
