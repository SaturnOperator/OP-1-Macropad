import mido

op1 = mido.open_input('OP-1 Midi Device')

# Receiving bits & print data
print("op1 receive():")
bits = int.from_bytes(op1.receive().bin(), 'big')
print(hex(bits))
print()

print("command")
print(hex((bits & 0xff0000) >> 0x10))
print("id")
print(hex((bits & 0xff00) >> 0x8))
print("value")
print(hex((bits & 0xff)))