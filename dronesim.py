import socket, Queue, threading, time, random, sys, json, select, GCSServer, datetime

ADDR = ("127.0.0.1", 43212)
id_ = sys.argv[1]

class DroneSim(threading.Thread):

	def __init__(self, id_):
		super(DroneSim, self).__init__()
		self.id = id_
		self.alive = threading.Event()
		self.alive.set()

	def run(self):
		self.socket_init()
		while self.alive.isSet():
			time.sleep(1)
			data = {
				"type": "status",
				"data": {
					"id": self.id,
					"lat": str(36.374092 + random.randrange(1, 10)*0.0001),
					"lng": str(127.365638 + random.randrange(1, 10)*0.0001),
					"alt": str(random.randrange(1, 10)),
					"activate": "on",
					"stream": "off",
					"battery": "95",
					"yaw": "45.0",
					"track": "off",
					"state": "ready",
					"image": "off",
					"lastUpdate": str(datetime.datetime.now()),
				},
			}
			# time.sleep(10)
			self.s.send(json.dumps(data))
			# recv_data = self.s.recv(2048)
			# print "data sent: ", data
			ready = select.select([self.s], [], [], 0.1)
			if ready[0]:
				recv_data = self.s.recv(2048)
				print "received data: ", recv_data
			else:
				continue
		self.s.close()
	def socket_init(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect(ADDR)
		self.s.setblocking(0)
		# self.s.settimeout(.2)
		print "connected to", ADDR


if __name__ == "__main__":
	drone = DroneSim(id_)
	drone.start()

	try:
		while True:
			time.sleep(.1)
	except KeyboardInterrupt:
		print "KeyboardInterrupt"

		drone.alive.clear()




