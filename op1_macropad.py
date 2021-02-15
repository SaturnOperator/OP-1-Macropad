import mido

op1 = mido.open_input('OP-1 Midi Device')

print(dir(op1))

while(1):
	print(op1.receive())