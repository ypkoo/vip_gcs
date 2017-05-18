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

	NEW, TERMINATE, ALEXA = range(3)

	def __init__(self, type_, data=None):
		self.type = type_
		self.data = data

class ServerReport(object):

	NEW, TEXT, TERMINATE, ALEXA = range(4)

	def __init__(self, type_, data=None):
		self.type = type_
		self.data = data