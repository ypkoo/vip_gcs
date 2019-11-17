"""
GCS Server for VIP project

Yoonpyo Koo (ypkoo@lanada.kaist.ac.kr)

Reference
Eli Bendersky's code sample (http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python/)
Pollable Queue http://chimera.labs.oreilly.com/books/1230000000393/ch12.html
"""

import socket, struct, threading, queue, select, json, sys, time, datetime
from VipQueueMsgType import *
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer


class PollableQueue(queue.Queue, object):
	def __init__(self):
		# super(PollableQueue, self).__init__()
		super(PollableQueue, self).__init__()

		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
		self.yaw = None

		""" Status Flags """
		self.activate = None
		self.battery = None
		self.state = None

		self.lastUpdate = None

		""" TO DO: reimplement using a queue """
		self.reportQueue = None 

	def get_info(self):
		info = {
			'id': self.id,
			'location': {'lat': self.lat, 'lng': self.lng, 'alt': self.alt},
			'yaw': self.yaw,
			'battery': self.battery,
			'state': self.state,
			'activate': self.activate,
			'lastUpdate': self.lastUpdate,
		}

		return info


class DroneClientThread(threading.Thread):

	def __init__(self, connection, q, send_to_all=None):
		super(DroneClientThread, self).__init__()
		self._socket = connection
		self._q = q
		self.send_to_all = send_to_all
		self.drone = None
		self.isM600 = None

		self.alive = threading.Event()
		self.alive.set()

		# self._isIdSet = False


	def run(self):
		while self.alive.isSet():
			try:
				raw_data = self._socket.recv(2048)
				if raw_data:
					try:
						data = json.loads(raw_data) # kokoga mondai
					except Exception as e:
						# print raw_data
						# print type(e)
						continue
					if self.drone:
						# print("[Drone client %s]" % self.drone.id, "update drone info", data)
						self._update_drone(data)
						
					else:
						self.drone = Drone(data["data"]["id"])
						self._update_drone(data)

						# self._q.put(ClientReport(ClientReport.NEW, data["data"]["id"]))
						self._q.put(ClientReport(ClientReport.NEW, self))
				else:
					# print "socket closed"
					self.alive.clear()
			except socket.error:
				self._socket.close()
				break

		""" Terminate the thread """
		self._terminate_thread()

	def _update_drone(self, data):
		if data["type"] == "status":
			
			self.drone.activate = data["data"]["activate"]
			self.drone.state = data["data"]["state"]
			self.drone.lastUpdate = data["data"]["lastUpdate"]

			if data["data"]["activate"] == "on":
				self.drone.lat = data["data"]["lat"]
				self.drone.lng = data["data"]["lng"]
				self.drone.alt = data["data"]["alt"]
				self.drone.yaw = data["data"]["yaw"]
				self.drone.battery = data["data"]["battery"]
			else:
				self.drone.lat = None
				self.drone.lng = None
				self.drone.alt = None
				self.drone.yaw = None
				self.drone.battery = None

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
		self.serverReportQueue = queue.Queue()

		self.alive = threading.Event()
		self.alive.set()

		""" Use custom Pollable queue to use select both for sockets and queues """
		self.clientReportQueue = PollableQueue()
		self.pollingList.append(self.clientReportQueue)

		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.socket.bind((host, port))
			self.socket.listen(5)
			self.pollingList.append(self.socket)
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, "Server initiated successfully."))

		except socket.error as ex:
			text = "Couldn't connect with the socket-server: %s\n terminating server" % ex
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
			sys.exit(1)

	def run(self):
		while self.alive.isSet():
			readable, writable, exceptional = select.select(self.pollingList, [], [], 1)
			for s in readable:

				if s is self.socket:
					""" New client """
					connection, address = self.socket.accept()
					print ("connection", connection, "address", address)

					self._create_client(connection, self.clientReportQueue)
			
				else:
					""" Message from a client """
					msg = s.get()
					print (msg)

					if msg.type == ClientReport.NEW:
						""" TODO: what if id already exists? """
						self.droneList.append(msg.data)
						text = 'A new drone %s is connected.' % msg.data.drone.id
						self.serverReportQueue.put(ServerReport(ServerReport.NEW, msg.data.drone.id))
						# self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
					elif msg.type == ClientReport.TERMINATE:
						if msg.data.drone is not None:
							text = 'Drone %s connection closed.' % msg.data.drone.id
							self.droneList.remove(msg.data)
							msg.data.join()
							# self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
							self.serverReportQueue.put(ServerReport(ServerReport.TERMINATE, msg.data.drone.id))
					


	def _create_client(self, connection, q):
		client = DroneClientThread(connection, q, self.send_to_all)
		# self.droneList.append(client)

		client.start()

	def send(self, id_, msg):
		msg = msg.encode() # Python3
		for drone in self.droneList:
			if drone.drone.id == id_:
				drone.send(msg)

	def drone_by_id(self, id_):
		for drone in self.droneList:
			if drone.drone.id == id_:
				return drone

	def send_to_all(self, msg):
		msg = msg.encode() # Python3
		for drone in self.droneList:
			drone.send(msg)


	""" TODO """
	def server_close(self):
		pass


if __name__ == "__main__":
	server = GCSSeverThread("127.0.0.1", 43212)
	server.start()

	try:
		while True:
			time.sleep(.1)
	except KeyboardInterrupt:
		print ("KeyboardInterrupt")


		server.alive.clear()
