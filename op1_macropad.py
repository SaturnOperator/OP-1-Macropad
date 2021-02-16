from rtmidi import MidiIn as rtMidiIn

class OP1(rtMidiIn):
	def __init__(self):
		# Connect to OP-1 for midi input
		if(self.find_port()):
			self.open_port(self.port)
			print("Connected to %s on port %d" % (self.get_port_name(self.port), self.port))

	def find_port(self):
		# Find the port that the OP-1 is on
		try:
			self.port = self.get_ports().index('OP-1 Midi Device')
			return 1
		except ValueError:
			print("Could not find OP-1")
			exit()

	def query(self):
		count = 0
		while count < 10:
			message = self.get_message()
			if(message):
				print(message[0])
				count += 1

	def close(self):
		print("Closed connection on port %d" % self.port)
		self.close_port()

op1 = OP1()
op1.query()
op1.close()
exit()



