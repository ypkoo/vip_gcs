#!/usr/bin/python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json

from VipQueueMsgType import ClientReport


class AlexaHandler(BaseHTTPRequestHandler, object):

	def __init__(self, q):
		# super(AlexaHandler, self).__init__()
		self._q = q


	def do_POST(self):
		# print 'headers:', self.headers
		length = int(self.headers['Content-Length'])
		data = self.rfile.read(length).decode('utf-8')
		json_msg = json.loads(str(data))
		# {"slots": {"CommandText": {"name": "CommandText", "value": "start"}}, "name": "Command"}

		if json_msg['name'] == "Command":
			print "Command"
			command = json_msg['slots']['CommandText']['value']
			print command
			if command == "start":
				self._q.put(ClientReport(ClientReport.Alexa, "start"))
			elif command == "go":
				self._q.put(ClientReport(ClientReport.Alexa, "go"))
			elif command == "stop":
				self._q.put(ClientReport(ClientReport.Alexa, "stop"))
			self.send_response(200)

			return


if __name__ == "__main__":
	PORT = 8000
	try:
		server = HTTPServer(('', PORT), AlexaHandler)
		print('Start server. port:', PORT)
		server.serve_forever()

	except KeyboardInterrupt:
		print('^C received, shutting down the web server')
		server.socket.close()
