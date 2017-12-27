"""
GCS Server for VIP project

Yoonpyo Koo (ypkoo@lanada.kaist.ac.kr)

Reference
Eli Bendersky's code sample (http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python/)
Pollable Queue http://chimera.labs.oreilly.com/books/1230000000393/ch12.html
"""

import socket, struct, threading, Queue, select, json, sys, time, datetime
from AlexaServer import make_alexa_handler_class
from VipQueueMsgType import *
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

RELAY_SERVER_ADDR = ('', '')


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
		self.stream = None
		self.battery = None
		self.track = None
		self.state = None
		self.image = None

		self.lastUpdate = None

		""" TO DO: reimplement using a queue """
		self.reportQueue = None 

	def get_info(self):
		info = {
			'id': self.id,
			'location': {'lat': self.lat, 'lng': self.lng, 'alt': self.alt},
			'yaw': self.yaw,
			'stream': self.stream,
			'battery': self.battery,
			'track': self.track,
			'state': self.state,
			'image': self.image,
			'activate': self.activate,
			'lastUpdate': self.lastUpdate,
		}

		return info

	def update_status(self, data):
		self.activate = data["data"]["activate"]
		self.stream = data["data"]["stream"]
		self.track = data["data"]["track"]
		self.state = data["data"]["state"]
		self.image = data["data"]["image"]
		self.lastUpdate = data["data"]["lastUpdate"]

		if data["data"]["activate"] == "on":
			self.lat = data["data"]["lat"]
			self.lng = data["data"]["lng"]
			self.alt = data["data"]["alt"]
			self.yaw = data["data"]["yaw"]
			self.battery = data["data"]["battery"]
		else:
			self.lat = None
			self.lng = None
			self.alt = None
			self.yaw = None
			self.battery = None


class GCSSeverThread(threading.Thread):
	"""
	GCS server thread. A GUI can communicate with a client thread
	by queuing and dequeuing queues in droneClientList.

	Sending a msg to a client:
		droneClientList[id].cmd_q.put(msg)
	Receiving a msg from a client:
		droneClientList[id].reply_q.get()
	"""


	def __init__(self):
		super(GCSSeverThread, self).__init__()
		self.droneList = []
		self.serverReportQueue = Queue.Queue()

		self.alive = threading.Event()
		self.alive.set()

		""" Use custom Pollable queue to use select both for sockets and queues """
		self.clientReportQueue = PollableQueue()
		self.pollingList.append(self.clientReportQueue)

		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.settimeout(5)
			self.socket.connect(RELAY_SERVER_ADDR)

			# Hello
			self.socket.send(json.dump({"src":"GCS",}))

			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, "Successfully connected to the relay server"))
			# self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			# self.serverReportQueue.put(ServerReport(ServerReport.TEXT, "Server initiated successfully."))

		except socket.error, msg:
			text = "Couldn't connect with the relay server: %s\n terminating server" % msg
			self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
			sys.exit(1)

	def run(self):
		while self.alive.isSet():
			
			recv_data = json.load(self.s.recv(2048))
			if recv_data != "":
				self.msg_handler(recv_data)
			else:
				text = "Connection to relay server closed: %s\n terminating server" % msg
				self.serverReportQueue.put(ServerReport(ServerReport.TEXT, text))
				sys.exit(1)


	def msg_handler(self, msg):
		# Wrong destination. Discard.
		if msg["dst"] != "GCS":
			return

		_id = msg["src"]
		payload = msg["payload"]

		if payload["type"] == "status":
			if self.drone_by_id(id_) == None:
				droneList.append(Drone(id_))
				self.serverReportQueue.put(ServerReport(ServerReport.NEW, _id))
			drone = self.drone_by_id(id_)
			drone.update_status(msg["payload"])
		elif payload["topic"] == "network":
			if payload["command"] == "disconnect":
				self.droneList.remove(self.drone_by_id(id_))
				self.serverReportQueue.put(ServerReport(ServerReport.TERMINATE, _id))



	def send(self, id_, payload):
		msg = {
			"src": "GCS",
			"dst": id_,
			"payload": payload,
		}
		self.socket.send(json.dump(msg))

	def drone_by_id(self, id_):
		for drone in self.droneList:
			if drone.drone.id == id_:
				return drone

	def send_to_all(self, msg):
		for drone in self.droneList:
			drone.send(msg)

	""" TODO """
	def server_close(self):
		pass


if __name__ == "__main__":
	server = GCSSeverThread()
	server.start()

	try:
		while True:
			time.sleep(.1)
	except KeyboardInterrupt:
		print "KeyboardInterrupt"

		server.alive.clear()
