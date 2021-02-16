from rtmidi import MidiIn as rtMidiIn

# Get midi input
midiInput = rtMidiIn()

# Find OP-1 port
# ValueError: 'OP-1 Midi Device' is not in list
try:
	op1Port = midiInput.get_ports().index('OP-1 Midi Device')
except ValueError:
	print("Could not find OP-1")
	exit()

# Connect to OP-1 for midi input
midiInput.open_port(op1Port)
print("Connected to %s on port %d" % (midiInput.get_port_name(op1Port), op1Port))

# Display first 10 actions
count = 0
while count < 10:
	message = midiInput.get_message()
	if(message):
		print(message[0])
		count += 1

# Close connection
midiInput.close_port()
print("Closed connection on port %d" % op1Port)