"""
GCS Server for VIP project

Yoonpyo Koo (ypkoo@lanada.kaist.ac.kr)

Reference
Eli Bendersky's code sample (http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python/)
"""

import socket, struct, threading, Queue

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


class Drone(object):

	def __init__(self, id):

		self.id = id

		""" Location Info """
		self.lat = None
		self.lng = None
		self.alt = None

		""" Status Flags """
		self.isFlying = None
		self.isTracking = None
		self.isLocating = None

	def get_info(self):
		info = {
			id: self.drone.id
			location: (self.drone.lat, self.drone.lng, self.drone.alt)
			isFlying = self.drone.isFlying
			isTracking = self.drone.isTracking
			isLocating = self.drone.isLocating
		}

		return info


class DroneClientThread(threading.Thread):

	def __init__(self, connection, id):
		super(DroneClientThread, self).__init__()
		self.socket = connection
		self.drone = Drone(id)
		self.cmd_q = Queue.Queue()
		self.reply_q = Queue.Queue()
		self.alive = threading.Event()
		self.alive.set()

		self.handlers = {
			Command.SEND: self._handle_SEND,
			Command.GET_INFO: self._handle_GET_INFO,
			Command.CLOSE: self._handle_CLOSE,
		}



	def run(self):
		while self.alive.isSet():
			try:
				cmd = self.cmd_q.get(True, 0.1)
				self.handlers[cmd.type](cmd)
			except Queue.Empty as e:
				continue


	def _handle_SEND(self):
		pass

	def _handle_GET_INFO(self):
		try:
			info = self.drone.get_info()
			self.reply_q.put(self._success_reply(info))
		except Exception, e:
			self.reply_q.put(self._error_reply(str(e)))


	def _error_reply(self, errstr):
		return Reply(Reply.ERROR, errstr)

	def _success_reply(self, data=None):
		return Reply(Reply.SUCCESS, data)




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
		self.droneClientList = []
		self.socket = socket(AF_INET, SOCK_STREAM)
		self.socket.bind((host, port))
		self.socket.listen(5)

	def run(self):
		while True:
			connection, address = self.socket.accept()
			print 'Server connected by', address

			_create_client(connection)


	def _create_client(self, connection):
		client = DroneClientThread()
		self.droneClientList.append(client)

		client.start()




