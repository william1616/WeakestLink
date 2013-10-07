import socket
import hashlib
import json

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	clientsocket.connect(('localhost', 1024))
except:
	print('error')
	
while True:
	msg = clientsocket.recv(4096)
	check = clientsocket.recv(40).decode('UTF-8')
	assert(hashlib.sha1(msg).hexdigest() == check)
	msg = msg.decode('UTF-8')
	variables = json.loads(msg)
	for i in variables:
		print(i + ' = ' + str(variables[i]))
