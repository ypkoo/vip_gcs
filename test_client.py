import socket, struct, threading, Queue, time


class TestClientThread(threading.Thread):


	def __init__(self, host, port):
		super(TestClientThread, self).__init__()
		
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.connect((host, port))
		except:
			print "socket init error"

	def run(self):
		while True:
			self.socket.sendall("test string")
			time.sleep(1)

			except KeyboardInterrupt:
				self.socket.close()
				sys.exit()


	def _create_client(self, connection):
		client = DroneClientThread()
		self.droneClientList.append(client)

		client.start()

if __name__ == "__main__":
	client = TestClientThread("127.0.0.1", 41234)
	client.start()